export class CheckoutPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    this.addressTextarea = page.locator('textarea[placeholder="Enter your full delivery address..."]');
    this.notesInput = page.locator('input[placeholder="Special instructions..."]');
    this.placeOrderButton = page.locator('button[type="submit"]');
  }

  async fillDetails(address, notes) {
    await this.addressTextarea.fill(address);
    if (notes) {
      await this.notesInput.fill(notes);
    }
  }

  async placeOrder() {
    await this.placeOrderButton.click();
  }
}
