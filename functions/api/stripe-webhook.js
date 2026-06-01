export async function onRequestPost(context) {
  const sig = context.request.headers.get('stripe-signature');
  const body = await context.request.text();
  let event;
  try { event = JSON.parse(body); } catch(e) { return new Response('Bad request', { status: 400 }); }
  if (event.type !== 'checkout.session.completed') return new Response('OK', { status: 200 });
  const session = event.data.object;
  const email = session.customer_details?.email;
  if (!email) return new Response('No email', { status: 200 });
  const PRODUCTS = {
    'price_1TcoCbAyXUYO1wJKzhOxxXHw': { file: 'first-90-days-italy-pack.pdf', title: 'First 90 Days in Italy Pack' },
    'price_1TcoDyAyXUYO1wJKrfBdg01j': { file: 'visa-bundle.pdf', title: 'Complete Italy Visa Bundle' },
    'price_1TcoJgAyXUYO1wJKF5PIzkiY': { file: 'tax-survival-guide.pdf', title: 'US-Italy Tax Survival Guide' },
    'price_1TcoK8AyXUYO1wJKZ6M2h8Rr': { file: 'jure-sanguinis-master-pack.pdf', title: 'Jure Sanguinis Master Pack' },
    'price_1TcoKgAyXUYO1wJKRBfSDvFR': { file: 'buying-property-italy.pdf', title: 'Buying Property in Italy Guide' },
    'price_1TcoLNAyXUYO1wJK5wj1jASf': { file: 'where-to-live-italy.pdf', title: 'Where to Live in Italy' },
    'price_1TcoMNAyXUYO1wJKiY4HLwQY': { file: 'all-access-bundle.pdf', title: 'Italy Relocation All-Access Bundle' }
  };
  const priceId = session.metadata?.price_id || 'price_1TcoCbAyXUYO1wJKzhOxxXHw';
  const product = PRODUCTS[priceId] || PRODUCTS['price_1TcoCbAyXUYO1wJKzhOxxXHw'];
  const downloadUrl = `https://italopedia.com/shop/downloads/${product.file}`;
  const emailRes = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${context.env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: 'Fabrizio at Italopedia <info@italopedia.com>',
      to: email,
      subject: `Your ${product.title} is here 🇮🇹`,
      html: `<div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;padding:40px 20px;color:#1a1610'>
        <div style='font-size:24px;font-weight:bold;margin-bottom:8px'>Italo<span style='color:#b83020'>pedia</span></div>
        <h2 style='margin-top:32px'>Your guide is ready.</h2>
        <p style='font-size:16px;line-height:1.6;color:#444'>Thank you for your purchase. Your <strong>${product.title}</strong> is ready to download.</p>
        <a href='${downloadUrl}' style='display:inline-block;background:#b83020;color:white;padding:14px 28px;text-decoration:none;border-radius:4px;font-size:16px;margin:24px 0'>Download Your Guide →</a>
        <p style='color:#888;font-size:14px;margin-top:32px;border-top:1px solid #eee;padding-top:16px'>Questions? Reply to this email.<br/>Fabrizio · Piedmont, Italy · <a href='https://italopedia.com' style='color:#b83020'>italopedia.com</a></p>
      </div>`
    })
  });
  return new Response('OK', { status: 200 });
}
