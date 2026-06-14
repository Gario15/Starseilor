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
  
  let heading-text = it.body.text
  let special = heading-text in special-headings
  let heading-body = upper(heading-text)
  
  if special {
    align(center, [#heading-body])
  } else {
    align(center, [#counter(heading).display() #heading-body])
  }
}

#show heading.where(level: 2): it => {
  set text(weight: "bold", size: 14pt)
  set par(first-line-indent: 1.25cm, leading: 1.5em, spacing: 12pt)
  
  let heading-text = it.body.text
  let modified-text = lower(heading-text)
  
  [#counter(heading).display() #modified-text]
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


#show figure.where(kind: "Times new roman"): it => {
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
      #{
      set par(leading: 1.5em, first-line-indent: 0cm, justify: true, spacing: 18pt)
      align(left, [Таблица #num - #text(weight: "bold")[#caption-text]])
      }
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
  Словарь.\
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

**Аддон (Add-on)** — дополнительное программное расширение для Blender, написанное на Python, которое добавляет новый функционал в интерфейс программы.

**API (Application Programming Interface)** — набор классов, методов и свойств, предоставляемых Blender для взаимодействия внешних скриптов и аддонов с внутренними данными сцены.

**Безье (Bézier)** — тип кривой, задаваемой опорными точками и касательными (ручками), обеспечивающий плавное изменение направления.

**Geometry Nodes** — система визуального процедурного моделирования в Blender, основанная на нодовом графе.

**Инстанс (Instance)** — копия объекта, ссылающаяся на исходные данные (меш, материал), что экономит память и позволяет массово размещать объекты без дублирования геометрии.

**Клипирование (Clipping)** — отсечение объектов, попадающих в заданную зону (например, у концов кривой), чтобы избежать наложения или выхода за границы.

**Коллекция (Collection)** — контейнер в Blender для группировки объектов сцены; аналог слоёв или папок.

**Модификатор (Modifier)** — неразрушающая операция, применяемая к объекту в порядке стека (например, Array, Curve, Subdivision Surface).

**Нод (Node)** — элемент визуального графа обработки данных в Geometry Nodes или шейдерах.

**Относительная позиция (Relative position)** — координата точки вдоль кривой, нормированная к интервалу [0, 1], где 0 — начало, 1 — конец.

**Полилиния (Polyline)** — ломаная линия, состоящая из прямолинейных сегментов между последовательными точками.

**PropertyGroup** — базовый класс в Blender API для создания групп пользовательских свойств, которые можно привязывать к объектам сцены.

**Ручка (Handle)** — управляющая точка касательной для сплайна Безье; типы: `AUTO` (автоматическая), `VECTOR` (прямолинейная), `ALIGNED` (симметричная).

**Сплайн (Spline)** — элемент кривой, представляющий собой непрерывную линию; кривая в Blender может содержать несколько сплайнов.

**Трансформация (Transformation)** — изменение положения (перемещение), вращения (поворот) или масштаба объекта.

**Утилиты (Utilities)** — вспомогательные функции, не связанные напрямую с интерфейсом или операторами, но используемые ими для расчётов, работы с коллекциями, генерации случайных чисел.

**Хендлер (Handler)** — функция обратного вызова, вызываемая при наступлении определённого события (например, изменение свойства, сохранение файла).

**Зерно (Seed)** — начальное число для генератора псевдослучайных чисел; при одинаковом зерне последовательность случайных значений повторяется.

**3D Viewport** — основное окно Blender для трёхмерного просмотра и редактирования сцены.