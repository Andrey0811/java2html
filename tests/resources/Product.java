/**
 * Класс продукции со свойствами <b>maker</b> и <b>price</b>.
 * @author Киса Воробьянинов
 * @version 2.1
*/
class Product
{
    /** Поле производитель */
    private String maker;

    /** Поле цена */
    public double price;

    /**
     * Конструктор - создание нового объекта
     * @see Product
     */
    Product()
    {
        setMaker("");
        price=0;
    }
}