package com.logistics.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class LoginPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    private final By usernameInput = By.cssSelector("input[placeholder='Enter username']");
    private final By passwordInput = By.cssSelector("input[placeholder='Enter password']");
    private final By submitButton = By.xpath("//button[@type='submit']");

    public LoginPage(WebDriver driver, WebDriverWait wait) {
        this.driver = driver;
        this.wait = wait;
    }

    public void navigateTo(String baseUrl) {
        driver.get(baseUrl + "/login");
    }

    public void login(String username, String password) {
        WebElement usernameElem = wait.until(ExpectedConditions.visibilityOfElementLocated(usernameInput));
        usernameElem.clear();
        usernameElem.sendKeys(username);

        WebElement passwordElem = driver.findElement(passwordInput);
        passwordElem.clear();
        passwordElem.sendKeys(password);

        WebElement submitBtn = driver.findElement(submitButton);
        submitBtn.click();
    }
}
