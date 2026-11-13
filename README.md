# КТ №2. UML-диаграммы интернет-магазина

**Дисциплина:** Архитектура корпоративных приложений  
**Выполнила:** Алакберова Симран Ахлиман  
**Группа:** 4П1.23

**Предметная область:** система управления заказами интернет-магазина.

В репозитории находятся четыре диаграммы. Они отображаются прямо на GitHub. Исходники PlantUML размещены в папке `uml`.

**[Открыть подробный отчет](./ОТЧЕТ_КТ2.md)**

## Диаграмма прецедентов

```mermaid
flowchart LR
  Buyer["Покупатель"]
  Admin["Администратор"]
  subgraph Shop["Система интернет-магазина"]
    UC1(["Просмотреть каталог"])
    UC2(["Добавить товар в корзину"])
    UC3(["Оформить заказ"])
    UC4(["Оплатить заказ"])
    UC5(["Проверить статус"])
    UC6(["Управлять товарами"])
    UC7(["Обработать заказ"])
  end
  Buyer --> UC1
  Buyer --> UC2
  Buyer --> UC3
  Buyer --> UC4
  Buyer --> UC5
  Admin --> UC6
  Admin --> UC7
  UC3 -.->|include| UC4
```

[Исходник PlantUML](./uml/usecase.puml)

## Диаграмма классов

```mermaid
classDiagram
  direction LR
  class Customer {
    +int id
    +String name
    +String email
    +placeOrder()
  }
  class Product {
    +int id
    +String title
    +decimal price
    +int stock
    +checkAvailability()
  }
  class Cart {
    +int id
    +addProduct()
    +removeProduct()
    +getTotal()
  }
  class CartItem {
    +int quantity
    +getSubtotal()
  }
  class Order {
    +int id
    +String status
    +decimal total
    +confirm()
  }
  class OrderItem {
    +int quantity
    +decimal unitPrice
  }
  class Payment {
    +int id
    +decimal amount
    +String status
    +pay()
  }
  Customer "1" --> "1" Cart : использует
  Customer "1" --> "0..*" Order : оформляет
  Cart "1" *-- "0..*" CartItem : содержит
  CartItem "*" --> "1" Product : товар
  Order "1" *-- "1..*" OrderItem : содержит
  OrderItem "*" --> "1" Product : товар
  Order "1" --> "0..1" Payment : оплачивается
```

[Исходник PlantUML](./uml/classes.puml)

## Диаграмма активностей

```mermaid
flowchart TD
  A((Начало)) --> B["Просмотр каталога"]
  B --> C["Добавление товаров в корзину"]
  C --> D["Оформление заказа"]
  D --> E{"Товары в наличии?"}
  E -- "Нет" --> F["Сообщить об отсутствии"]
  F --> Z((Конец))
  E -- "Да" --> G["Создать заказ"]
  G --> H["Выполнить оплату"]
  H --> I{"Оплата успешна?"}
  I -- "Нет" --> J["Показать ошибку оплаты"]
  J --> Z
  I -- "Да" --> K["Изменить статус заказа"]
  K --> L["Отправить подтверждение"]
  L --> Z
```

[Исходник PlantUML](./uml/activity.puml)

## Диаграмма последовательности

```mermaid
sequenceDiagram
  actor Buyer as Покупатель
  participant UI as Веб-приложение
  participant Orders as Сервис заказов
  participant DB as База данных
  participant Pay as Платежный сервис
  Buyer->>UI: Оформить корзину
  UI->>Orders: createOrder(items)
  Orders->>DB: проверить остатки
  DB-->>Orders: сведения о наличии
  alt Товары в наличии
    Orders->>DB: сохранить заказ
    DB-->>Orders: orderId
    Orders->>Pay: charge(amount)
    Pay-->>Orders: результат оплаты
    alt Оплата успешна
      Orders->>DB: статус = PAID
      Orders-->>UI: заказ подтвержден
    else Ошибка оплаты
      Orders->>DB: статус = PAYMENT_FAILED
      Orders-->>UI: ошибка оплаты
    end
  else Товаров нет в наличии
    Orders-->>UI: заказ не оформлен
  end
  UI-->>Buyer: показать результат
```

[Исходник PlantUML](./uml/sequence.puml)
