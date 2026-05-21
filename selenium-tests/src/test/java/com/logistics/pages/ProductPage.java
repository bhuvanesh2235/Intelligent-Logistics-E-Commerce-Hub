package com.logistics.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.Select;
import org.openqa.selenium.support.ui.WebDriverWait;

public class ProductPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    // Locators on Products Listing Page
    private final By addProductBtn = By.xpath("//button[contains(text(), 'Add Product')]");
    
    // Locators on Add Product Form Page
    private final By skuInput = By.xpath("//input[@placeholder='e.g. ELEC-001']");
    private final By nameInput = By.xpath("//input[@placeholder='Product name']");
    private final By descTextarea = By.xpath("//textarea[@placeholder='Product description...']");
    private final By costInput = By.xpath("//label[contains(text(), 'Cost Price')]/following-sibling::input");
    private final By priceInput = By.xpath("//label[contains(text(), 'Selling Price')]/following-sibling::input");
    private final By stockInput = By.xpath("//label[contains(text(), 'Stock Quantity')]/following-sibling::input");
    private final By categoryInput = By.xpath("//label[contains(text(), 'Category ID')]/following-sibling::input");
    private final By warehouseInput = By.xpath("//label[contains(text(), 'Warehouse ID')]/following-sibling::input");
    private final By weightInput = By.xpath("//label[contains(text(), 'Weight')]/following-sibling::input");
    private final By importanceSelect = By.xpath("//label[contains(text(), 'Importance')]/following-sibling::select");
    private final By submitBtn = By.xpath("//button[@type='submit']");

    public ProductPage(WebDriver driver, WebDriverWait wait) {
        this.driver = driver;
        this.wait = wait;
    }

    public void clickAddProductButton() {
        WebElement btn = wait.until(ExpectedConditions.elementToBeClickable(addProductBtn));
        btn.click();
    }

    public void createNewProduct(String sku, String name, String desc, String cost, String price, 
                                 String stock, String categoryId, String warehouseId, String weight, 
                                 String importance) {
        wait.until(ExpectedConditions.visibilityOfElementLocated(skuInput)).sendKeys(sku);
        driver.findElement(nameInput).sendKeys(name);
        driver.findElement(descTextarea).sendKeys(desc);
        driver.findElement(costInput).sendKeys(cost);
        driver.findElement(priceInput).sendKeys(price);
        driver.findElement(stockInput).sendKeys(stock);
        driver.findElement(categoryInput).sendKeys(categoryId);
        if (warehouseId != null && !warehouseId.isEmpty()) {
            driver.findElement(warehouseInput).sendKeys(warehouseId);
        }
        driver.findElement(weightInput).sendKeys(weight);
        
        Select select = new Select(driver.findElement(importanceSelect));
        try {
            select.selectByValue(importance);
        } catch (Exception e) {
            select.selectByVisibleText(importance);
        }

        driver.findElement(submitBtn).click();
    }
}
