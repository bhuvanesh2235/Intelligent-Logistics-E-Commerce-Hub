package com.logistics.pages;

import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

public class DashboardPage {

    private final WebDriver driver;
    private final WebDriverWait wait;

    // Sidebar Links (using partial or exact link text since they contain emojis + labels)
    private final By productsLink = By.xpath("//a[contains(@href, '/products')]");
    private final By adminDashboardLink = By.xpath("//a[contains(@href, '/admin')]");
    private final By aiForecastLink = By.xpath("//a[contains(@href, '/forecast')]");
    private final By damageDetectionLink = By.xpath("//a[contains(@href, '/damage')]");

    // Page Specific Headers for validation
    private final By pageTitle = By.className("page-title");
    private final By kpiGrid = By.className("kpi-grid");

    public DashboardPage(WebDriver driver, WebDriverWait wait) {
        this.driver = driver;
        this.wait = wait;
    }

    public void navigateToProducts() {
        WebElement link = wait.until(ExpectedConditions.elementToBeClickable(productsLink));
        link.click();
    }

    public void navigateToAdminDashboard() {
        WebElement link = wait.until(ExpectedConditions.elementToBeClickable(adminDashboardLink));
        link.click();
    }

    public void navigateToAiForecast() {
        WebElement link = wait.until(ExpectedConditions.elementToBeClickable(aiForecastLink));
        link.click();
    }

    public void navigateToDamageDetection() {
        WebElement link = wait.until(ExpectedConditions.elementToBeClickable(damageDetectionLink));
        link.click();
    }

    public String getPageTitleText() {
        WebElement titleElem = wait.until(ExpectedConditions.visibilityOfElementLocated(pageTitle));
        return titleElem.getText();
    }

    public boolean isKpiGridVisible() {
        try {
            WebElement kpi = wait.until(ExpectedConditions.visibilityOfElementLocated(kpiGrid));
            return kpi.isDisplayed();
        } catch (Exception e) {
            return false;
        }
    }
}
