export class ProductCatalogPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.productCards = page.locator('.product-card');
    this.cartLink = page.locator('a[href="/cart"]');
  }

  async navigate() {
    await this.page.goto('/products');
  }

  async addFirstProductToCart() {
    await this.productCards.first().waitFor();
    const addButton = this.productCards.first().locator('button:has-text("Add")');
    await addButton.click();
  }

  async navigateToCart() {
    await this.cartLink.click();
  }
}
