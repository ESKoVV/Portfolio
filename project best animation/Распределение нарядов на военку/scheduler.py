# scheduler.py
from datetime import datetime, timedelta
import json
import random
from database import Database

class Scheduler:
    def __init__(self, db):
        self.db = db
    
    def get_all_mondays(self):
        """Get all Mondays between start and end dates"""
        start_date_str = self.db.get_setting('start_date')
        end_date_str = self.db.get_setting('end_date')
        
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        mondays = []
        current_date = start_date
        
        # Find first Monday
        while current_date <= end_date:
            if current_date.weekday() == 0:  # Monday
                mondays.append(current_date.strftime('%Y-%m-%d'))
                break
            current_date += timedelta(days=1)
        
        # Add remaining Mondays
        if mondays:
            current_date = datetime.strptime(mondays[0], '%Y-%m-%d') + timedelta(weeks=1)
            while current_date <= end_date:
                mondays.append(current_date.strftime('%Y-%m-%d'))
                current_date += timedelta(weeks=1)
        
        return mondays
    
    def generate_schedule(self):
        # Clear existing schedule first
        self.db.save_schedule([])
        
        # ВАЖНО: Получаем АКТУАЛЬНЫЕ данные из базы с текущими счетчиками
        people = self.db.get_people()
        if not people:
            return []
        
        # Создаем изменяемый список всех людей
        all_people = [list(p) for p in people]
        
        mondays = self.get_all_mondays()
        guard_frequency = int(self.db.get_setting('guard_frequency'))
        schedule = []
        
        for week_num, monday in enumerate(mondays):
            # Проверяем, должна ли эта неделя иметь наряды
            has_guard = (week_num % guard_frequency) == 0
            
            # 1) ДЕЖУРСТВО: выбираем из НЕ командиров
            duty_candidates = [p for p in all_people if not p[6]]  # not commander
            duty_person = self.select_person_by_min_count(duty_candidates, 1, [])  # duty_count
            
            # 2) ВПИ: выбираем из НЕ командиров, исключая дежурного
            vpi_exclude = [duty_person[0]] if duty_person else []
            vpi_candidates = [p for p in all_people if not p[6] and p[0] not in vpi_exclude]
            vpi_person = self.select_person_by_min_count(vpi_candidates, 2, [])  # vpi_count
            
            # 3) НАРЯД: выбираем из НЕ командиров и НЕ раненых, исключая дежурного и ВПИ
            guard_people = []
            if has_guard:
                guard_count = int(self.db.get_setting('guard_count'))
                guard_exclude = []
                if duty_person:
                    guard_exclude.append(duty_person[0])
                if vpi_person:
                    guard_exclude.append(vpi_person[0])
                
                guard_candidates = [
                    p for p in all_people 
                    if not p[6] and not p[5] and p[0] not in guard_exclude  # not commander, not wounded, not excluded
                ]
                
                # Выбираем guard_count человек с минимальным guard_count
                guard_people = self.select_multiple_people_by_min_count(guard_candidates, 3, guard_count)
            
            # ОБНОВЛЯЕМ СЧЕТЧИКИ В ЛОКАЛЬНОМ МАССИВЕ
            if duty_person:
                self.increment_local_counter(all_people, duty_person[0], 1)  # duty_count
            if vpi_person:
                self.increment_local_counter(all_people, vpi_person[0], 2)  # vpi_count
            for guard_name in guard_people:
                self.increment_local_counter(all_people, guard_name, 3)  # guard_count
            
            schedule.append((
                monday,
                duty_person[0] if duty_person else "",
                vpi_person[0] if vpi_person else "",
                guard_people
            ))
        
        # ОБНОВЛЯЕМ СЧЕТЧИКИ В БАЗЕ ДАННЫХ
        self.update_database_counters(all_people)
        
        return schedule
    
    def select_person_by_min_count(self, people, count_index, exclude_names):
        """
        Выбирает одного человека с наименьшим счетчиком
        """
        if not people:
            return None
        
        # Фильтруем по исключениям
        available = [p for p in people if p[0] not in exclude_names]
        if not available:
            return None
        
        # Находим минимальное значение счетчика
        min_count = min(p[count_index] for p in available)
        
        # Все с минимальным счетчиком
        min_count_people = [p for p in available if p[count_index] == min_count]
        
        # Случайный выбор из минимальных
        return random.choice(min_count_people) if min_count_people else None
    
    def select_multiple_people_by_min_count(self, people, count_index, count_needed):
        """
        Выбирает несколько человек с наименьшим счетчиком
        """
        if not people or count_needed <= 0:
            return []
        
        # Находим минимальное значение счетчика
        min_count = min(p[count_index] for p in people)
        
        # Все с минимальным счетчиком
        min_count_people = [p for p in people if p[count_index] == min_count]
        
        # Если людей с минимальным счетчиком меньше чем нужно, берем всех
        if len(min_count_people) <= count_needed:
            selected_people = [p[0] for p in min_count_people]
        else:
            # Случайно выбираем нужное количество из минимальных
            selected_people = [p[0] for p in random.sample(min_count_people, count_needed)]
        
        return selected_people
    
    def increment_local_counter(self, people, person_name, count_index):
        """Увеличивает счетчик в локальном массиве"""
        for person in people:
            if person[0] == person_name:
                person[count_index] += 1
                break
    
    def update_database_counters(self, people):
        """Обновляет счетчики в базе данных после генерации расписания"""
        people_data = []
        for person in people:
            name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander = person
            people_data.append((name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander))
        
        self.db.save_people(people_data)
    
    def swap_people(self, date, role, current_person, new_person):
        schedule = self.db.get_schedule()
        updated_schedule = []
        
        for sched_date, duty_person, vpi_person, guard_people in schedule:
            if sched_date == date:
                if role == 'duty':
                    duty_person = new_person
                elif role == 'vpi':
                    vpi_person = new_person
                elif role == 'guard':
                    if current_person in guard_people:
                        index = guard_people.index(current_person)
                        guard_people[index] = new_person
            
            updated_schedule.append((sched_date, duty_person, vpi_person, guard_people))
        
        self.db.save_schedule(updated_schedule)
        return updated_schedule
    
    def get_available_people_for_date(self, date, exclude_people):
        """Get people available for a specific date (not wounded, not commanders, and not in exclude_people)"""
        all_people = self.db.get_people()
        available = []
        
        for person in all_people:
            name, duty_count, vpi_count, guard_count, is_senior, is_wounded, is_commander = person
            # Exclude wounded, commanders, and people already assigned that day
            if not is_wounded and not is_commander and name not in exclude_people:
                available.append(name)
        
        return available