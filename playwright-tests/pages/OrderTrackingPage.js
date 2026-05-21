export class OrderTrackingPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
    // Orders Page
    this.orderNumbers = page.locator('td div:has-text("ORD-")'); // Matches order number text
    this.trackingNumbers = page.locator('td:has-text("TRK-")'); // Matches tracking number text
    
    // Tracking Page
    this.trackingInput = page.locator('input[placeholder*="tracking number"]');
    this.trackButton = page.locator('button[type="submit"]:has-text("Track")');
    this.trackingResultHeader = page.locator('div:has-text("Tracking Number") + div');
  }

  async navigateToOrders() {
    await this.page.goto('/orders');
  }

  async getLatestOrderNumber() {
    await this.page.waitForSelector('table tbody tr');
    return await this.page.locator('td').first().locator('div').innerText();
  }

  async getLatestTrackingNumber() {
    await this.page.waitForSelector('table tbody tr');
    // The tracking number column is the 6th column (0-indexed 5) or matching the text TRK-
    const trackingCell = this.page.locator('td:has-text("TRK-")').first();
    return await trackingCell.innerText();
  }

  async navigateToTracking() {
    await this.page.goto('/tracking');
  }

  async trackShipment(trackingNumber) {
    await this.trackingInput.fill(trackingNumber);
    await this.trackButton.click();
  }

  async getTrackedNumber() {
    await this.page.waitForSelector('text=Delivery Progress');
    const text = await this.page.locator('div:has-text("TRK-")').first().innerText();
    const match = text.match(/TRK-[A-Z0-9-]+/i);
    return match ? match[0] : '';
  }
}
