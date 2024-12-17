import PySimpleGUI as sg


# Создание и укладка элементов окна
layout = [
   [sg.Text('Текст', key='-Text-label-')],
   [sg.Multiline('', key='-Text-', expand_x=True, expand_y=True)],
   [sg.Text('Вопрос', key='-Question-label-')],
   [sg.Input('', key='-Question-')],
   [sg.Button('Получить ответ')],
   [sg.Text('Ответ', key='-Answer-label-', visible=False)],
   [sg.Text('', key='-Answer-', font=('Arial Bold', 13), visible=False)],
]
# Создание окна
window = sg.Window('', layout, resizable=True, size=(700, 700), finalize=True)

# Обработка событий окна, пока оно не будет закрыто
while True:
   event, values = window.read()
   # Событие закрытие окна
   if event == sg.WINDOW_CLOSED:
       break
   # Событие при нажатии на кнопку для 'Получить ответ'
   elif event == 'Получить ответ':
       window['-Answer-label-'].update(visible=True)
       window['-Answer-'].update(
           question_answer(values['-Text-'], values['-Question-']),
           visible=True
       )

window.close()