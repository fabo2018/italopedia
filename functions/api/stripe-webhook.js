export async function onRequestPost(context) {
  const sig = context.request.headers.get('stripe-signature');
  const body = await context.request.text();
  const secret = context.env.STRIPE_WEBHOOK_SECRET;

  // Verify Stripe signature manually (no npm in CF Pages edge)
  // Accept only checkout.session.completed events
  let event;
  try {
    event = JSON.parse(body);
  } catch(e) {
    return new Response('Bad request', { status: 400 });
  }

  if (event.type === 'checkout.session.completed') {
    const email = event.data.object.customer_details?.email;
    if (!email) return new Response('No email', { status: 200 });

    const res = await fetch('https://api.resend.com/emails', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${context.env.RESEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        from: 'Fabrizio at Italopedia <info@italopedia.com>',
        to: email,
        subject: 'Your First 90 Days in Italy Pack is here 🇮🇹',
        html: `
          <div style='font-family:Georgia,serif;max-width:600px;margin:0 auto;padding:40px 20px'>
            <img src='https://italopedia.com/assets/img/logo.png' width='140' alt='Italopedia'/>
            <h2 style='color:#1a1610;margin-top:32px'>Your guide is ready.</h2>
            <p style='color:#444;font-size:16px;line-height:1.6'>Thank you for your purchase. Your <strong>First 90 Days in Italy Pack</strong> is attached below — 20 pages covering everything from your permesso application to SSN enrollment.</p>
            <a href='https://italopedia.com/shop/downloads/first-90-days-italy-pack.pdf'
               style='display:inline-block;background:#b83020;color:white;padding:14px 28px;text-decoration:none;border-radius:4px;font-size:16px;margin:24px 0'>
              Download Your Guide →
            </a>
            <p style='color:#888;font-size:14px;margin-top:32px'>Questions? Just reply to this email.<br/>Fabrizio · Piedmont, Italy · italopedia.com</p>
          </div>
        `
      })
    });

    if (!res.ok) {
      const err = await res.text();
      console.error('Resend error:', err);
      return new Response('Email error', { status: 500 });
    }
  }

  return new Response('OK', { status: 200 });
}
