#set page(
  paper: "a4",
  margin: (
    left: 25mm,
    right: 10mm,
    top: 15mm,
    bottom: 25mm
  )
)

#set text(
  font: "Times new roman",
  size: 12pt,
  lang: "ru"
)

#set par(
  leading: 1.5em,
  first-line-indent: 1.25cm,
  justify: true,
  spacing: 18pt
)

#let special-headings = (
  "Введение", "Заключение", "Содержание", 
  "Список использованных источников", "Глоссарий", 
  "Список аббревиатур", "Приложения"
)


#show heading.where(level: 1): it => {
  pagebreak()
  set text(weight: "bold", size: 14pt)
  set par(first-line-indent: 0pt, leading: 1.5em, spacing: 12pt)
  
  if it.body in special-headings {
    align(center, text(style: "Times new roman", upper(it.body)))
  } else {
    align(center, it.body)
  }
}

#show heading.where(level: 2): it => {
  set text(weight: "bold", size: 14pt)
  set par(first-line-indent: 1.25cm, leading: 1.5em, spacing: 12pt)
  align(center, it.body)
}

#set heading(numbering: (..values) => {
  let nums = values.pos()
  if nums.len() == 1 {
    return str(nums.first())
  } else if nums.len() == 2 {
    return str(nums.first()) + "." + str(nums.at(1))
  } else {
    // Ручное объединение без map
    let result = ""
    for (i, num) in nums.enumerate() {
      if i > 0 {
        result += "."
      }
      result += str(num)
    }
    return result
  }
})

#set list(
  marker: [—],
  indent: 2cm,
  body-indent: 0.7cm,
)


#show figure.where(kind: "image"): it => {
  v(6pt)
  set text(size: 12pt, style: "italic")
  set par(first-line-indent: 0pt, leading: 1.5em)
  align(center, it)
  v(6pt)
}

#set table(
  stroke: (x, y) => {
    if y == 0 {
      (top: 1pt, bottom: 1pt, left: 0.5pt, right: 0.5pt)
    } else {
      (bottom: 0.5pt, left: 0.5pt, right: 0.5pt)
    }
  },
  inset: 4pt,
)

#let table-caption(body, caption-text, num) = {
  context {
    text(size: 12pt)[
      #v(6pt)
      #align(right, [Таблица #num])
      #align(center, text(weight: "bold")[#caption-text])
      #v(6pt)
    ]
  }
  body
}
#let code-main(content) = {
  set text(font: "Times new roman", size: 12pt)
  set par(leading: 1em, first-line-indent: 0pt)
  raw(content, lang: "text", block: true)
}

#let code-app(content) = {
  set text(font: "Times new roman ", size: 8pt)
  set par(leading: 1em, first-line-indent: 0pt)
  raw(content, lang: "text", block: true)
}

// ---------------------- Содержание ----------------------
#let outline-custom = {
  set text(size: 12pt, weight: "regular")
  set par(first-line-indent: 0pt)
  outline(
    title: [Содержание],
    indent: 1em,
    depth: 2
  )
}


// ---------------------- Приложения ----------------------
#let appendix-start(title, letter) = {
  pagebreak()
  set text(size: 14pt, weight: "bold")
  align(center, [Приложение #letter])
  v(-8pt)
  align(center, title)
  v(12pt)
}


#align(center, text(weight: "bold", size: 12pt)[
  #v(12pt)
  Государственное бюджетное среднее профессиональное образовательное учреждение\
  Республики Хакасия\
  «Хакасский политехнический колледж»
])

#v(180pt)

#align(center, text(weight: "bold", size: 14pt)[
  Руководство оператора.
])

#v(180pt)
#align(right, text(size: 12pt)[
Студент группы ИС(ТП)-31 

Горев А.П.

Дата: 08.06.2026
])
#v(130pt)

#align(center, text(size: 12pt)[
  Абакан 2026
])

#set page(numbering: "1", number-align: center)

= Аннотация
Настоящий документ содержит сведения, необходимые системному администратору для установки, настройки и сопровождения аддона Starselor для Blender. Руководство описывает требования к оборудованию и ПО, структуру компонентов, процедуру развёртывания на компьютерах пользователей, проверку работоспособности и процесс обновления.

#outline-custom

= Общие сведения о программе
== Назначение программы
Starselor – это аддон для программы трёхмерного моделирования Blender, предназначенный для автоматизированного размещения объектов вдоль кривых. Основные возможности:
- Размещение объектов-шаблонов в точках кривой
- Размещение объектов-шаблонов вдоль рёбер/сегментов кривой
- Случайное масштабирование и вращение размещаемых объектов
- Подразделение кривой без изменения исходных данных
- Ограничение диапазона размещения
- Клипирование концов кривой по расстоянию
- Автоматическое создание отдельных коллекций для каждой кривой
- Поддержка независимых настроек для каждого объекта-кривой в сцене
== Условия применения
Корпоративное использование Starselor предполагает наличие установленного Blender версии 4.0.0 или выше. Аддон не требует подключения к интернету и работает полностью локально.
== Требования к оборудованию и программному обеспечению для работы аддона Starselor
#table-caption(
  table(
  columns: (auto, auto, auto),
  table.header(
    [*Параметр*], [*Минимальные требования*], [*Рекомендуемые требования*],
  ),
  [ОС], [Windows 10, macOS 11, Linux (Ubuntu 20.04+)], [Windows 11, macOS 13+, Linux],
  [Blender], [4.0.0], [4.2+ LTS],
  [Процессор], [x86-64, 2 ядра], [4+ ядра],
  [ОЗУ], [4 ГБ], [16+ ГБ],
  [Диск], [50 МБ под аддон], [100 МБ + место для кэша Blender],
  [Видеокарта], [Любая с OpenGL 3.3], [Дискретная GPU],
  ),
  "Требования к компонентам",
  1
)
Требования к инфраструктуре организации:
#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Компонент*], [*Требование*],
    ),
    [Сеть], [Не требуется],
    [Права доступа], [Запись в директорию аддонов Blender],
    [Лицензирование], [Blender – GPL, аддон распространяется свободно],
  ),
  "Дополнительные требования к компонентам",
  2,
)
= Структура программы
Аддон Starselor состоит из следующих компонентов:
#table-caption(
  table(
    columns: (auto, auto, auto),
    table.header(
      [*Компонент*], [*Файл*], [*Описание*],
    ),
    [Модуль инициализации], [__init__.py], [Регистрация аддона в Blender, определение метаданных, импорт подмодулей],
    [Модуль операторов], [operators.py], [Реализация действий пользователя: размещение объектов, очистка экземпляров, переключение типов ручек кривой],
    [Модуль панелей], [panels.py], [Определение интерфейса пользователя в боковой панели 3D View],
    [Модуль свойств], [properties.py], [Определение структур данных для хранения настроек],
    [Модуль утилит], [utils.py], [Вспомогательные функции: работа с коллекциями, случайные трансформации, расчёт позиций на сегментах],
  ),
  "Структура файлов аддона",
  3,
)
*Архитектура хранения данных:*

Каждый объект кривой в Blender получает следующие динамические свойства:
```
bpy.types.Object
├── main_object
│   ├── curv – ссылка на кривую
│   ├── ObjectsInPoints – шаблон для точек
│   └── ObjectsInEdges – шаблон для рёбер
├── curve_operftion
│   ├── SubdiveCurveSet – уровень подразделения
│   ├── DelCurvePoints – скрыть точечные объекты
│   └── DelCurveEdges – скрыть рёберные объекты
├── curve_equals
│   ├── EqualLengths – использовать диапазон
│   ├── StartEdge / EndEdge – границы диапазона
│   ├── ClipOn – включить клипирование
│   └── ClipDistance – дистанция клипа
├── curve_option_container
│   ├── point – настройки для точечных объектов
│   └── edge – настройки для рёберных объектов
 edge_spacing_props
│   ├── use_distance / edge_distance – интервал по расстоянию
│   ├── use_count / edge_count – количество объектов
│   └── offset_start / offset_end – отступы от концов
└── starselor_collection_name – имя коллекции экземпляров
```
*Коллекции экземпляров:*

Размещённые объекты сохраняются в коллекциях с префиксом `Starselor_`, за которым следует имя исходной кривой, невалидные символы заменяются на `"_"`.

Пример: кривая Road_Curve.001 → коллекция Starselor_Road_Curve_001
= Установка программы на компьютер пользователя
== Ручная установка
- Запустите Blender версии 4.0.0 или выше.
- Перейдите в меню Edit → Preferences → Add-ons.
- Нажмите кнопку Install в правом верхнем углу.
- В диалоговом окне выберите ZIP-архив или папку аддона Starselor.
- Найдите аддон в списке.
- Установите флажок слева от названия для активации аддона.
- Нажмите Save Preferences для сохранения настроек.
== Автоматическая установка для развёртывания через SCCM/групповые политики
*Копирование файлов в директорию аддонов Blender:*

Базовые пути для различных ОС:
#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*ОС*], [*Путь к директории аддонов*],
    ),
    [Windows], [%APPDATA%\\Blender Foundation\\Blender\\4.0\\scripts\\addons\\],
    [Windows (портативная установка)], [[Blender_install_dir]\\4.0\\scripts\\addons\\],
    [macOS], [~/Library/Application Support/Blender/4.0/scripts/addons/],
    [Linux], [~/.config/blender/4.0/scripts/addons/],
  ),
  "Пути установки аддона Blender",
  4,
)
Скрипт для массового развёртывания Windows, PowerShell: