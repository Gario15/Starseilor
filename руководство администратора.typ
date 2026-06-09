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
  
  // Преобразуем содержимое заголовка в строку
  let heading-text = it.body.text
  let special = heading-text in special-headings
  let heading-body = if special { upper(heading-text) } else { heading-text }
  
  if special {
    align(center, [#heading-body])
  } else {
    align(center, [#counter(heading).display() #heading-body])
  }
}
#show heading.where(level: 2): it => {
  set text(weight: "bold", size: 14pt)
  set par(first-line-indent: 1.25cm, leading: 1.5em, spacing: 12pt)
  align(center, [#counter(heading).display() #it.body])
}

#set heading(numbering: (..values) => {
  let nums = values.pos()
  if nums.len() == 1 {
    return str(nums.first())
  } else if nums.len() == 2 {
    return str(nums.first()) + "." + str(nums.at(1))
  } else {
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

// Исправленные функции: принимают raw-блок и используют его текстовое содержимое
#let code-main(raw-content) = {
  set text(font: "Times new roman", size: 12pt)
  set par(leading: 1em, first-line-indent: 0pt)
  raw(lang: "text", block: true, raw-content.text)
}

#let code-app(raw-content) = {
  set text(font: "Times new roman", size: 8pt)
  set par(leading: 1em, first-line-indent: 0pt)
  raw(lang: "text", block: true, raw-content.text)
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
  Государственное бюджетное профессиональное образовательное учреждение\
  Республики Хакасия\
  «Хакасский политехнический колледж»
])

#v(180pt)

#align(center, text(weight: "bold", size: 14pt)[
  Руководство администратора.\
  Starseilor — аддон для Blender
])

#v(180pt)
#align(right, text(size: 12pt)[
  Студент группы ИС(ТП)-31 \
  Горев А.П. \
  Дата: 09.06.2026
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

Starselor – это аддон (расширение) для программы трёхмерного моделирования Blender, предназначенный для автоматизированного размещения объектов вдоль кривых. Основные возможности:

- Размещение объектов-шаблонов в точках кривой (Point Objects)
- Размещение объектов-шаблонов вдоль рёбер/сегментов кривой (Edge Objects)
- Случайное масштабирование и вращение размещаемых объектов
- Подразделение кривой без изменения исходных данных
- Ограничение диапазона размещения (Start/End)
- Клипирование концов кривой по расстоянию
- Автоматическое создание отдельных коллекций для каждой кривой
- Поддержка независимых настроек для каждого объекта-кривой в сцене

== Условия применения

Корпоративное использование Starselor предполагает наличие установленного Blender версии 4.0.0 или выше. Аддон не требует подключения к интернету и работает полностью локально.

== Требования к оборудованию и программному обеспечению

=== Требования к компонентам для работы аддона Starselor

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
  "Требования к оборудованию и ПО",
  1
)

=== Требования к инфраструктуре организации

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Компонент*], [*Требование*],
    ),
    [Сеть], [Не требуется (локальная работа)],
    [Права доступа], [Запись в директорию аддонов Blender],
    [Лицензирование], [Blender – GPL, аддон распространяется свободно],
  ),
  "Требования к инфраструктуре",
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

*Архитектура хранения данных*

Каждый объект кривой в Blender получает следующие динамические свойства:

#code-main(```
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
├── edge_spacing_props
│   ├── use_distance / edge_distance – интервал по расстоянию
│   ├── use_count / edge_count – количество объектов
│   └── offset_start / offset_end – отступы от концов
└── starselor_collection_name – имя коллекции экземпляров
```)

*Коллекции экземпляров*

Размещённые объекты сохраняются в коллекциях с префиксом `Starselor_`, за которым следует имя исходной кривой. Невалидные символы (точки, пробелы) заменяются на `_`.

Пример: кривая `Road_Curve.001` → коллекция `Starselor_Road_Curve_001`

= Установка программы на компьютер пользователя

== Ручная установка

- Запустите Blender версии 4.0.0 или выше.
- Перейдите в меню **Edit → Preferences → Add-ons**.
- Нажмите кнопку **Install** в правом верхнем углу.
- В диалоговом окне выберите ZIP-архив или папку аддона Starselor.
- Найдите аддон в списке (категория **3D View**, название **Starselor**).
- Установите флажок слева от названия для активации аддона.
- Нажмите **Save Preferences** для сохранения настроек.

== Автоматическая установка для развёртывания через SCCM/групповые политики

*Копирование файлов в директорию аддонов Blender*

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

*Скрипт для массового развёртывания (Windows PowerShell)*

#code-main(```
# deploy_starselor.ps1
$blenderVersion = "4.0"
$addonsPath = "$env:APPDATA\Blender Foundation\Blender\$blenderVersion\scripts\addons"
$sourcePath = "\\server\share\Starselor"

if (!(Test-Path $addonsPath)) {
    New-Item -ItemType Directory -Path $addonsPath -Force
}

Copy-Item -Path "$sourcePath\Starselor" -Destination $addonsPath -Recurse -Force
Write-Host "Starselor deployed to $addonsPath"
```)

*Скрипт для автоматической активации аддона (Python)*

#code-main(```
# enable_starselor.py
import bpy

addon_name = "Starselor"
if addon_name not in bpy.context.preferences.addons:
    bpy.ops.preferences.addon_enable(module=addon_name)
    bpy.ops.wm.save_userpref()
    print(f"Add-on {addon_name} enabled")
```)

Запуск скрипта из командной строки:

`blender --background --python enable_starselor.py`


= Проверка работоспособности программы

После установки выполните следующие проверки для каждого модуля.

== Модуль 1: Загрузка и активация аддона

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [Открыть Blender → Edit → Preferences → Add-ons], [Аддон "Starselor" присутствует в списке],
    [Включить аддон (установить флажок)], [Флажок установлен, сообщения об ошибках отсутствуют],
    [Нажать Save Preferences], [Настройки сохранены],
    [Перезапустить Blender], [Аддон остаётся активным],
  ),
  "Проверка загрузки и активации аддона",
  5,
)

**Критерий успеха:** Аддон активен и не вызывает ошибок в консоли.

== Модуль 2: Отображение панели интерфейса

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [Создать новую сцену (File → New → General)], [Сцена создана],
    [Добавить кривую (Shift+A → Curve → Bezier Curve)], [Кривая появилась в сцене],
    [Выделить кривую], [Панель инструментов справа (N-панель)],
    [Перейти на вкладку "Starselor" в боковой панели], [Отображаются все подпанели аддона],
  ),
  "Проверка отображения панели интерфейса",
  6,
)

**Критерий успеха:** Панель "Starselor" видна и содержит все разделы.

== Модуль 3: Размещение объектов на точках кривой

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [Создать простой 3D-объект (Shift+A → Mesh → Cube)], [Куб в сцене],
    [В панели Starselor выбрать этот куб в поле "Point Object"], [Объект выбран],
    [Нажать кнопку "Place Objects"], [В коллекции `Starselor_{имя_кривой}` появляются копии куба в каждой точке кривой],
  ),
  "Проверка размещения объектов на точках кривой",
  7,
)

**Критерий успеха:** Количество размещённых объектов равно количеству точек кривой.

== Модуль 4: Размещение объектов на рёбрах кривой

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [Создать объект-шаблон (например, сфера)], [Сфера в сцене],
    [В панели Starselor выбрать сферу в поле "Edge Object"], [Объект выбран],
    [В разделе "Edge Spacing" включить "Use Count" и установить Count=3], [Настройки применены],
    [Нажать "Place Objects"], [На каждом сегменте кривой размещены 3 сферы с правильной ориентацией],
  ),
  "Проверка размещения объектов на рёбрах кривой",
  8,
)

**Критерий успеха:** Объекты размещены на каждом сегменте с правильной ориентацией.

== Модуль 5: Случайные трансформации

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [В разделе "Object Options" выбрать "Point Object"], [Отображаются настройки для точечных объектов],
    [Включить "Random Scale" и установить Seed=1], [Настройки применены],
    [Нажать "Place Objects"], [Объекты имеют разный масштаб],
    [Изменить Seed и снова разместить объекты], [Масштаб объектов изменился],
  ),
  "Проверка случайных трансформаций",
  9,
)

**Критерий успеха:** Объекты получают случайные масштаб и/или поворот.

== Модуль 6: Ограничение диапазона и клипирование

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [В разделе "Placement Range" включить "Use Range"], [Появились ползунки Start/End],
    [Установить Start=0.2, End=0.8], [Диапазон ограничен],
    [Разместить объекты], [Объекты отсутствуют в первой и последней 1/5 части кривой],
    [Включить "Enable Clip" и установить Distance=0.5], [Объекты не размещаются на расстоянии 0.5 ед. от концов],
  ),
  "Проверка ограничения диапазона и клипирования",
  10,
)

**Критерий успеха:** Размещение объектов ограничено заданным диапазоном.

== Модуль 7: Подразделение кривой

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [В разделе "Curve Options" установить "Subdivide"=2], [Кривая подразделяется без изменения исходного объекта],
    [Разместить объекты], [Количество объектов увеличивается пропорционально подразделению],
    [Установить "Subdivide"=0], [Кривая возвращается к исходному состоянию],
  ),
  "Проверка подразделения кривой",
  11,
)

**Критерий успеха:** Подразделение работает без потери исходных данных кривой.

== Модуль 8: Очистка экземпляров

#table-caption(
  table(
    columns: (auto, auto),
    table.header(
      [*Действие*],
      [*Ожидаемый результат*],
    ),
    [Нажать кнопку "Clear" в панели Starselor], [Все объекты в коллекции `Starselor_{имя_кривой}` удалены],
    [Нажать "Clear All Starselor Collections"], [Удалены ВСЕ коллекции с префиксом `Starselor_` во всей сцене],
  ),
  "Проверка очистки экземпляров",
  12,
)

**Критерий успеха:** Все экземпляры объектов удалены без влияния на исходные шаблоны.

= Обновление программы

== Определение текущей версии

Текущая версия аддона указана в:

- Файле `__init__.py` – параметр `"version": (1, 5)`
- Интерфейсе Blender: **Edit → Preferences → Add-ons → Starselor**

== Ручное обновление

- Сохраните все текущие проекты.
- Откройте **Edit → Preferences → Add-ons**.
- Найдите Starselor в списке.
- Снимите флажок для деактивации аддона.
- Нажмите кнопку **Remove** (если доступна) или удалите папку аддона вручную.
- Нажмите **Install…** и выберите новый ZIP-архив аддона.
- Активируйте аддон и нажмите **Save Preferences**.

== Автоматическое обновление (скрипт Windows PowerShell)

#code-main(```
# update_starselor.ps1
param(
    [string]$blenderVersion = "4.0",
    [string]$addonsPath = "$env:APPDATA\Blender Foundation\Blender\$blenderVersion\scripts\addons",
    [string]$sourcePath = "\\server\share\Starselor\latest"
)

$targetPath = Join-Path $addonsPath "Starselor"
if (Test-Path $targetPath) {
    Remove-Item -Path $targetPath -Recurse -Force
}
Copy-Item -Path "$sourcePath\Starselor" -Destination $addonsPath -Recurse -Force
Write-Host "Update completed"
```)

== Откат версии

При обнаружении проблем:

- Деактивируйте текущую версию аддона.
- Удалите папку `Starselor` из директории аддонов.
- Установите предыдущую версию из резервной копии.
- Активируйте аддон.

*Рекомендация:* храните архив предыдущих версий в корпоративном репозитории.

= Заключение

В данном руководстве изложены все необходимые сведения для административной поддержки аддона Starselor: от установки до обновления и проверки работоспособности. Аддон полностью локальный, не требует сетевых подключений и легко развёртывается в корпоративной среде благодаря простой файловой структуре и поддержке автоматической установки. Все функциональные модули проходят проверку по единым критериям, что позволяет оперативно выявлять неисправности.

= Список использованных источников

1. Blender Foundation. Blender Documentation: Add-on Development. – URL: https://docs.blender.org/manual/en/latest/extensions/addons.html (дата обращения: 09.06.2026).
2. Starselor. Исходный код аддона. – Репозиторий организации, 2026.
3. ГОСТ 2.105-95. Единая система конструкторской документации. Общие требования к текстовым документам. – М.: Стандартинформ, 1995.

= Приложения

#appendix-start("Листинги основных модулей аддона", "А")
#code-app(```
# __init__.py (фрагмент)
bl_info = {
    "name": "Starselor",
    "author": "Glue",
    "version": (1, 5),
    "blender": (4, 0, 0),
    "location": "View3D > Toolbar > Starselor",
    "description": "Размещение объектов вдоль кривой",
    "category": "3D View",
}

def register():
    properties.register()
    operators.register()
    panels.register()

def unregister():
    panels.unregister()
    operators.unregister()
    properties.unregister()
    utils.clear_all_instances()
```)

#appendix-start("Пример файла конфигурации для массового развёртывания", "Б")
#code-app(```
# config.ps1
$env:BLENDER_USER_SCRIPTS = "D:\BlenderScripts"
$addon_source = "\\fs\public\Starselor.zip"
$blender_path = "C:\Program Files\Blender Foundation\Blender 4.0\blender.exe"

# Установка аддона через командную строку
& $blender_path --background --python enable_starselor.py
```)

#appendix-start("Перечень кодов ошибок и способов их устранения", "В")
#code-app(`
Код / сообщение                         Причина                               Решение
----------------------------------------------------------------------------------------------------
"Active object is not a curve"         Выбран не кривой объект               Выбрать кривую
"No objects to place"                  Не выбраны шаблоны                    Выбрать Point или Edge Object
"Error placing objects"                Нулевая длина сегмента                Проверить кривую
ReferenceError                          Объект был удалён                     Перезапустить Blender
Панель не отображается                  Не выбран объект кривой               Выделить кривую
`)