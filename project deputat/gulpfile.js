const gulp = require('gulp');
const sass = require('gulp-sass')(require('sass'));
const autoprefixer = require('gulp-autoprefixer');

// Компиляция SCSS
gulp.task('styles', () => {
  return gulp.src('scss/main.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(autoprefixer())
    .pipe(gulp.dest('css'));
});

// Слежение за изменениями
gulp.task('watch', () => {
  gulp.watch('scss/**/*.scss', gulp.series('styles'));
});

gulp.task('default', gulp.parallel('styles', 'watch'));