from tensorflow.keras.models import load_model

model = load_model('my_kickstarter_model.keras')
model.save('my_kickstarter_model.h5')
print("✅ Модель сохранена как my_kickstarter_model.h5")