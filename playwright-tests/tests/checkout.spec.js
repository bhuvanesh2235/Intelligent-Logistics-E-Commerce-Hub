import { test, expect } from '@playwright/test';
import { LoginPage } from '../pages/LoginPage.js';
import { ProductCatalogPage } from '../pages/ProductCatalogPage.js';
import { CartPage } from '../pages/CartPage.js';
import { CheckoutPage } from '../pages/CheckoutPage.js';
import { OrderTrackingPage } from '../pages/OrderTrackingPage.js';

test.describe('E2E Checkout Flow', () => {
  test('should complete login, browse, add to cart, checkout, and track shipment successfully', async ({ page }) => {
    const loginPage = new LoginPage(page);
    const catalogPage = new ProductCatalogPage(page);
    const cartPage = new CartPage(page);
    const checkoutPage = new CheckoutPage(page);
    const trackingPage = new OrderTrackingPage(page);

    // 1. Login
    console.log('Navigating to login page...');
    await loginPage.navigate();
    console.log('Submitting customer credentials...');
    await loginPage.login('john_doe', 'Admin@123');

    // Verify login by asserting we are on the homepage
    await expect(page).toHaveURL('/');
    console.log('Logged in successfully!');

    // 2. Browse & Add to Cart
    console.log('Navigating to product catalog...');
    await catalogPage.navigate();
    console.log('Adding first product to cart...');
    await catalogPage.addFirstProductToCart();

    // 3. View Cart
    console.log('Opening shopping cart...');
    await catalogPage.navigateToCart();
    await expect(page).toHaveURL('/cart');
    console.log('Proceeding to checkout...');
    await cartPage.proceedToCheckout();

    // 4. Checkout Details & Placement
    await expect(page).toHaveURL('/checkout');
    console.log('Filling shipping details...');
    await checkoutPage.fillDetails(
      '789 Automated Playwright Boulevard, QA Zone 42',
      'Delivery details filled automatically by Playwright E2E Runner.'
    );
    console.log('Placing order...');
    await checkoutPage.placeOrder();

    // 5. Order & Tracking Verification
    console.log('Redirecting to orders page...');
    await expect(page).toHaveURL('/orders');
    
    console.log('Retrieving tracking number from orders table...');
    const trackingNumber = await trackingPage.getLatestTrackingNumber();
    console.log(`Tracking number retrieved: ${trackingNumber}`);
    
    expect(trackingNumber).not.toBeNull();
    expect(trackingNumber).toContain('TRK-');

    // 6. Track Shipment
    console.log('Navigating to tracking page...');
    await trackingPage.navigateToTracking();
    console.log(`Submitting tracking number: ${trackingNumber}`);
    await trackingPage.trackShipment(trackingNumber);

    console.log('Verifying tracking output matches...');
    const trackedNumText = await trackingPage.getTrackedNumber();
    expect(trackedNumText).toBe(trackingNumber);
    console.log('E2E Checkout & Tracking flow completed successfully!');
  });
});
