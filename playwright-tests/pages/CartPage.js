export class CartPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.checkoutButton = page.locator('button:has-text("Proceed to Checkout")');
  }

  async proceedToCheckout() {
    await this.checkoutButton.click();
  }
}
