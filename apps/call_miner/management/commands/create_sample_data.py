import time
import hashlib
from datetime import datetime, timedelta
import random
from django.conf import settings
from django.utils import timezone
from django.core.management.base import BaseCommand, CommandError
from firebase_admin import auth
from apps.call_miner.models import Organization, OrganizationAPIKey, Analyst, Agent, Topic, Customer, Conversation, User

COMMON_PASSWORD = 'tell_me_long'
TOPIC_DATA = [
    {
        "name": "Order Status",
        "description": "Inquiries about the current status of customer orders, including tracking updates, estimated "
                       "delivery times, and delays."
    },
    {
        "name": "Returns and Exchanges",
        "description": "Questions and requests related to the return or exchange of purchased items, including policy "
                       "clarifications, refund processing, and replacement shipments."},
    {
        "name": "Sizing and Fit",
        "description": "Customers seeking advice on sizing, fit, and measurements for clothing and footwear to ensure "
                       "proper selection before purchase."
    },
    {
        "name": "Product Availability",
        "description": "Requests for information on stock availability, restocking schedules, and pre-order options "
                       "for specific items."
    },
    {
        "name": "Discounts and Promotions",
        "description": "Inquiries about current or upcoming sales, discount codes, loyalty rewards, and special offers."
    },
    {
        "name": "Payment and Billing",
        "description": "Issues or questions about payment methods, billing discrepancies, refunds or installment plans."
    },
    {
        "name": "Shipping Issues",
        "description": "Problems related to shipping, including incorrect addresses, lost packages, expedited "
                       "shipping options, and international delivery queries."
    },
    {
        "name": "Account Management",
        "description": "Assistance with account-related matters such as password resets, updating personal details, "
                       "and troubleshooting login problems."},
    {
        "name": "Product Quality",
        "description": "Feedback or complaints about the quality of received items, such as material defects, "
                       "incorrect items, or missing components."
    },
    {
        "name": "Styling Assistance",
        "description": "Customers seeking recommendations or advice on how to style certain pieces, "
                       "outfit combinations, or accessorizing for specific occasions."
    },
]
CONVERSATION_DATA = [
    {
        "transcript": """<customer>: Hi, I’m calling to check on my order status. 
                          <agent>: Sure, can I have your order number, please?
                          <customer>: It’s 12345.
                          <agent>: Thank you. I see your order is on its way and should arrive by Tuesday.
                          <customer>: Great, thank you!
                          <agent>: Is there anything else I can help you with today?
                          <customer>: Nope, that’s all. Thanks!""",
        "topics": ["1"],
        "summary": "The customer called to check on the status of their order. The agent confirmed it is in transit and will arrive by Tuesday. No further issues were raised."
    },
    {
        "transcript": """<customer>: Hi, I received a dress, but it’s the wrong size.
                          <agent>: I’m sorry to hear that. Would you like to exchange it for the correct size?
                          <customer>: Yes, please. It’s a size small, but I need a medium.
                          <agent>: Let me process that for you. I’ll email you a return label for the incorrect size, and we’ll send out the medium.
                          <customer>: Thank you so much!
                          <agent>: You’re welcome. Anything else I can assist you with?
                          <customer>: No, that’s it. Thanks.""",
        "topics": ["2", "3"],
        "summary": "The customer received the wrong size dress and requested an exchange. The agent facilitated the return process and arranged for the correct size to be sent."
    },
    {
        "transcript": """<customer>: Hello, I’m interested in an item that’s out of stock. Do you know when it will be available again?
                          <agent>: Can you tell me the product name or ID?
                          <customer>: Sure, it’s the Classic Leather Jacket, ID 67890.
                          <agent>: Thank you. It looks like we’ll restock that item next month.
                          <customer>: Alright, I’ll check back then. Thank you!
                          <agent>: You’re welcome!""",
        "topics": ["4"],
        "summary": "The customer inquired about the restocking date of a leather jacket. The agent informed them it would be available next month."
    },
    {
        "transcript": """<customer>: Hi, I have a question about my payment for an order.
                          <agent>: Sure, what seems to be the issue?
                          <customer>: I was charged twice for the same item.
                          <agent>: Let me look into that for you. I see the duplicate charge. I’ll initiate a refund immediately.
                          <customer>: Thanks, that’s a relief.
                          <agent>: No problem. It should reflect in your account within 5-7 business days.
                          <customer>: Perfect, thank you.
                          <agent>: Happy to help!""",
        "topics": ["6"],
        "summary": "The customer reported a duplicate charge for an item. The agent identified the issue and initiated a refund, providing an estimated timeline for the resolution."
    },
    {
        "transcript": """<customer>: Hello, my package hasn’t arrived yet, and it’s past the estimated delivery date.
                          <agent>: I apologize for the inconvenience. Can I have your order number?
                          <customer>: It’s 54321.
                          <agent>: Thank you. I see there’s a delay due to weather conditions. It should arrive in 2-3 days.
                          <customer>: Alright, I’ll wait. Thanks for letting me know.
                          <agent>: Of course. Anything else I can help with?
                          <customer>: No, that’s it.""",
        "topics": ["5", "1"],
        "summary": "The customer called about a delayed package. The agent explained the reason for the delay and provided a new estimated delivery date."
    },
    {
        "transcript": """<customer>: Hi, I’m having trouble logging into my account.
                          <agent>: Can you tell me what’s happening when you try to log in?
                          <customer>: It says my password is incorrect, but I’m sure it’s right.
                          <agent>: Let me reset your password. You’ll receive an email shortly to set a new one.
                          <customer>: Got it. Thank you for your help.
                          <agent>: You’re welcome!""",
        "topics": ["7"],
        "summary": "The customer couldn’t log into their account due to a password issue. The agent reset the password, and the customer will receive an email to set a new one."
    },
    {
        "transcript": """<customer>: Hello, I wanted to report an issue with a jacket I ordered.
                          <agent>: What seems to be the issue?
                          <customer>: The zipper broke the first time I wore it.
                          <agent>: I’m sorry to hear that. We can send a replacement or issue a refund. Which would you prefer?
                          <customer>: A replacement, please.
                          <agent>: Consider it done. The new jacket will arrive within 5 business days.
                          <customer>: Thank you so much!
                          <agent>: You’re welcome!""",
        "topics": ["8", "2"],
        "summary": "The customer reported a defective zipper on a jacket. The agent arranged for a replacement to be sent within 5 business days."
    },
    {
        "transcript": """<customer>: Hi, I have a question about your current promotions.
                          <agent>: Sure, we’re offering 20% off on orders over $100 and free shipping on all orders.
                          <customer>: Great, I’ll place my order now. Thanks for the info!
                          <agent>: You’re welcome. Happy shopping!""",
        "topics": ["5"],
        "summary": "The customer inquired about current promotions. The agent provided details about discounts and free shipping offers."
    },
    {
        "transcript": """<customer>: Hello, can you help me find a size guide for your jeans?
                          <agent>: Absolutely. I’ll send you a link to our size guide for jeans.
                          <customer>: Thanks. I want to make sure I get the right fit.
                          <agent>: Happy to help! Let me know if you have other questions.""",
        "topics": ["3"],
        "summary": "The customer requested a size guide for jeans. The agent provided a link to the size guide to assist with proper selection."
    },
    {
        "transcript": """<customer>: Hi, I need some ideas for a formal event. Can you help?
                          <agent>: Of course. Are you looking for dresses or suits?
                          <customer>: Dresses, preferably something elegant.
                          <agent>: I recommend checking out our evening gowns section. I can email you some options.
                          <customer>: That would be great. Thank you!
                          <agent>: You’re welcome!""",
        "topics": ["10"],
        "summary": "The customer sought styling advice for a formal event. The agent suggested evening gowns and offered to email recommendations."
    },
    {
        "transcript": """<customer>: Hi, I ordered a pair of shoes, but they don’t fit.
                          <agent>: I’m sorry to hear that. Would you like to return them or exchange for another size?
                          <customer>: I’d like to exchange them for a size larger, please.
                          <agent>: Sure, can I have your order number?
                          <customer>: It’s 34567.
                          <agent>: Thank you. I’ll email you a return label, and we’ll send out the new size right away.
                          <customer>: Perfect, thank you!
                          <agent>: You’re welcome!""",
        "topics": ["2", "3"],
        "summary": "The customer reported that the shoes they ordered didn’t fit and requested an exchange. The agent processed the return and arranged for a larger size to be shipped."
    },
    {
        "transcript": """<customer>: Hello, I want to know if the item I’ve been eyeing will be back in stock.
                          <agent>: Of course. Can you share the product name or ID?
                          <customer>: Yes, it’s the Red Velvet Dress, ID 98765.
                          <agent>: Thank you. It looks like it will be restocked in two weeks.
                          <customer>: Great! I’ll wait for it. Thanks for checking.
                          <agent>: Happy to help!""",
        "topics": ["4"],
        "summary": "The customer inquired about the restocking schedule for a specific dress. The agent informed them it would be available in two weeks."
    },
    {
        "transcript": """<customer>: Hi, I saw a double charge on my credit card for my last order.
                          <agent>: I apologize for the inconvenience. Can you provide your order number so I can check?
                          <customer>: Sure, it’s 12389.
                          <agent>: Thank you. I see the duplicate charge. I’ll initiate a refund immediately.
                          <customer>: Thanks! That’s great.
                          <agent>: No problem. You’ll receive the refund within 5-7 business days.""",
        "topics": ["6"],
        "summary": "The customer reported a double charge for their order. The agent confirmed the issue and initiated a refund with an expected timeline of 5-7 business days."
    },
    {
        "transcript": """<customer>: Hi, I have an event tomorrow, but my package hasn’t arrived yet!
                          <agent>: I’m sorry to hear that. Let me check the status for you. Can I have your order number?
                          <customer>: It’s 54389.
                          <agent>: Thank you. It seems there was a delay. We’ll expedite shipping and ensure it reaches you by tomorrow morning.
                          <customer>: Thank you so much!
                          <agent>: Happy to help!""",
        "topics": ["5", "1"],
        "summary": "The customer expressed urgency over a delayed package. The agent confirmed the issue and arranged expedited shipping to meet the deadline."
    },
    {
        "transcript": """<customer>: Hi, I need help resetting my account password.
                          <agent>: Of course. Can I verify your email address first?
                          <customer>: Yes, it’s customer123@example.com.
                          <agent>: Thank you. I’ve sent a password reset email. Follow the link to set a new password.
                          <customer>: Got it. Thanks a lot!
                          <agent>: You’re welcome. Let me know if you need further assistance.""",
        "topics": ["7"],
        "summary": "The customer needed help resetting their account password. The agent sent a reset email and guided them on next steps."
    },
    {
        "transcript": """<customer>: Hello, the jacket I ordered came with a torn sleeve.
                          <agent>: I’m so sorry to hear that. Would you like a replacement or a refund?
                          <customer>: A replacement, please.
                          <agent>: Let me arrange that for you. The new jacket will arrive within 5 business days.
                          <customer>: Thank you for resolving this quickly.
                          <agent>: My pleasure.""",
        "topics": ["8", "2"],
        "summary": "The customer received a damaged jacket and requested a replacement. The agent processed the replacement and provided a delivery timeline."
    },
    {
        "transcript": """<customer>: Hi, I’m wondering if there’s a loyalty discount for my next purchase?
                          <agent>: Yes, loyalty members receive a 15% discount on all items.
                          <customer>: That’s great! How do I apply it?
                          <agent>: It’s automatically applied at checkout when you’re logged into your account.
                          <customer>: Perfect. Thanks for the info!
                          <agent>: Happy to help!""",
        "topics": ["5"],
        "summary": "The customer inquired about loyalty discounts. The agent explained the 15% discount and how it is applied at checkout."
    },
    {
        "transcript": """<customer>: Hi, I need styling advice for an upcoming beach party.
                          <agent>: Of course! Are you looking for casual or dressy outfits?
                          <customer>: Something casual but stylish.
                          <agent>: I recommend our summer collection of lightweight shirts and shorts. I can send you some links.
                          <customer>: That would be helpful. Thanks!
                          <agent>: You’re welcome!""",
        "topics": ["10"],
        "summary": "The customer requested styling advice for a beach party. The agent suggested items from the summer collection and offered to send links."
    },
    {
        "transcript": """<customer>: Hi, I’d like to return a pair of jeans that don’t fit.
                          <agent>: I’m sorry to hear that. Would you like to exchange them or get a refund?
                          <customer>: A refund, please.
                          <agent>: Sure. Can I have your order number?
                          <customer>: It’s 23456.
                          <agent>: Thank you. I’ll email you a return label, and the refund will be processed once we receive the item.
                          <customer>: Thanks for your help.
                          <agent>: Anytime!""",
        "topics": ["2", "3"],
        "summary": "The customer wanted to return a pair of jeans that didn’t fit. The agent provided a return label and explained the refund process."
    },
    {
        "transcript": """<customer>: Hello, I’d like to know if the Red Dress is still available in size medium.
                          <agent>: Let me check for you. Can you confirm the product ID?
                          <customer>: It’s 56789.
                          <agent>: Thank you. Unfortunately, it’s currently out of stock in that size. Would you like to be notified when it’s back?
                          <customer>: Yes, please.
                          <agent>: I’ve set up a notification for you. You’ll receive an email as soon as it’s restocked.
                          <customer>: That’s great. Thanks!
                          <agent>: You’re welcome!""",
        "topics": ["4"],
        "summary": "The customer inquired about the availability of a dress in a specific size. The agent set up a restock notification for the customer."
    },
    {
        "transcript": """<customer>: Hi, I placed an order two days ago, but I need to change the delivery address.
                          <agent>: Let me check if the order is still in processing. Can I have your order number?
                          <customer>: It’s 99871.
                          <agent>: Thank you. The order hasn’t shipped yet, so I can update the address. Can you provide the new address?
                          <customer>: Yes, it’s 123 New Street, Springfield.
                          <agent>: Got it. The address has been updated, and your order will arrive on schedule.
                          <customer>: Perfect. Thanks for your help.
                          <agent>: You’re welcome!""",
        "topics": ["1", "5"],
        "summary": "The customer called to update the delivery address for their order. The agent confirmed the update as the order hadn’t shipped yet."
    },
    {
        "transcript": """<customer>: Hi, I received an email about a 20% discount, but I don’t see it applied at checkout.
                          <agent>: Let me look into that. Can you confirm if the email includes a promo code?
                          <customer>: Yes, it’s SAVE20.
                          <agent>: Thank you. Please enter this code at checkout under 'Apply Promo Code'.
                          <customer>: Oh, I missed that. Thanks for the clarification.
                          <agent>: You’re welcome. Let me know if you have further questions.""",
        "topics": ["5"],
        "summary": "The customer needed help applying a promo code. The agent explained where to enter it during checkout."
    },
    {
        "transcript": """<customer>: Hello, I need to return a jacket because it’s not what I expected.
                          <agent>: I’m sorry to hear that. Can you describe the issue?
                          <customer>: The color looks different from what was shown online.
                          <agent>: I understand. I’ll email you a return label, and you can choose between a refund or a different item.
                          <customer>: A refund would be great. Thanks.
                          <agent>: Done. The refund will be processed upon receiving the jacket.""",
        "topics": ["2", "8"],
        "summary": "The customer returned a jacket due to color differences. The agent provided a return label and initiated a refund process."
    },
    {
        "transcript": """<customer>: Hi, I need assistance with my account. I’ve been locked out.
                          <agent>: I’m sorry about that. Can I verify your email address to reset it for you?
                          <customer>: It’s customer123@example.com.
                          <agent>: Thank you. I’ve reset your account and sent a recovery email. You can set a new password from there.
                          <customer>: Got it. Thanks for your help.
                          <agent>: My pleasure!""",
        "topics": ["7"],
        "summary": "The customer was locked out of their account. The agent verified their details and reset the account, providing recovery instructions."
    },
    {
        "transcript": """<customer>: Hello, I was wondering if the Beige Trench Coat will be back in stock soon?
                          <agent>: Let me check for you. Can you confirm the product ID?
                          <customer>: Yes, it’s 78543.
                          <agent>: Thank you. It’s scheduled to be restocked in three weeks.
                          <customer>: Great! I’ll check back then. Thanks.
                          <agent>: Anytime!""",
        "topics": ["4"],
        "summary": "The customer inquired about the restock date of a trench coat. The agent provided an estimated timeline for its availability."
    },
    {
        "transcript": """<customer>: Hi, I’d like some recommendations for a business-casual outfit.
                          <agent>: Of course! Are you looking for something specific, like shirts or trousers?
                          <customer>: Both, actually. I want something versatile.
                          <agent>: I recommend our slim-fit shirts and chinos. I’ll email you some suggestions.
                          <customer>: That would be great. Thank you!
                          <agent>: My pleasure.""",
        "topics": ["10"],
        "summary": "The customer requested styling advice for business-casual attire. The agent provided recommendations and offered to send suggestions via email."
    },
    {
        "transcript": """<customer>: Hi, I ordered a bag, but the strap is broken.
                          <agent>: I’m sorry to hear that. Would you prefer a replacement or a refund?
                          <customer>: A replacement, please.
                          <agent>: Sure. Can I have your order number?
                          <customer>: It’s 45123.
                          <agent>: Thank you. The replacement will be shipped today and should arrive in 3 days.
                          <customer>: Thank you for resolving this quickly.
                          <agent>: You’re welcome!""",
        "topics": ["2", "8"],
        "summary": "The customer received a bag with a broken strap. The agent processed a replacement, ensuring it would be shipped immediately."
    },
    {
        "transcript": """<customer>: Hello, I haven’t received my package, and it’s been two weeks.
                          <agent>: I’m very sorry for the delay. Can I have your order number?
                          <customer>: It’s 67891.
                          <agent>: Thank you. It seems the package was lost in transit. I’ll issue a replacement order immediately.
                          <customer>: Thanks. When can I expect it?
                          <agent>: The replacement will arrive in 5-7 business days.""",
        "topics": ["5"],
        "summary": "The customer reported a missing package. The agent confirmed it was lost and issued a replacement order with a new delivery timeline."
    },
    {
        "transcript": """<customer>: Hi, I need help picking a dress for an upcoming gala.
                          <agent>: Certainly! Do you have a preferred style or color in mind?
                          <customer>: Something formal and elegant in black.
                          <agent>: I recommend our collection of evening gowns. I can email you specific options.
                          <customer>: That would be great. Thanks for your help.
                          <agent>: Anytime!""",
        "topics": ["10"],
        "summary": "The customer sought advice for a formal gala outfit. The agent suggested evening gowns and offered to email options."
    },
    {
        "transcript": """<customer>: Hello, I’m seeing a charge on my credit card that I don’t recognize.
                          <agent>: Let me check that for you. Can you confirm the order number or date of the charge?
                          <customer>: I think it’s from last week, but I didn’t order anything.
                          <agent>: I see the issue. It was a system error. I’ll issue a full refund immediately.
                          <customer>: Thank you for fixing this.
                          <agent>: You’re welcome!""",
        "topics": ["6"],
        "summary": "The customer reported an unrecognized charge. The agent confirmed it was a system error and processed a full refund."
    },
    {
        "transcript": """<customer>: Hi, I placed an order for a coat, but I forgot to use my promo code.
                          <agent>: No problem. Can you share your order number and the promo code?
                          <customer>: Sure, it’s 91234 and the code is WINTER20.
                          <agent>: Thank you. I’ve applied the discount, and you’ll receive the difference as a refund within 3-5 business days.
                          <customer>: That’s amazing. Thanks for the help!
                          <agent>: My pleasure!""",
        "topics": ["5", "6"],
        "summary": "The customer forgot to use a promo code when placing their order. The agent applied the discount retroactively and issued a refund."
    },
    {
        "transcript": """<customer>: Hello, I ordered a shirt, but I realized I chose the wrong size.
                          <agent>: Would you like to exchange it for the correct size?
                          <customer>: Yes, please. I need a size large instead of medium.
                          <agent>: I’ll send you a return label, and the large size will be shipped once we receive the return.
                          <customer>: Perfect. Thanks so much.
                          <agent>: You’re welcome!""",
        "topics": ["2", "3"],
        "summary": "The customer ordered the wrong size shirt and requested an exchange. The agent provided a return label and arranged for the correct size to be shipped."
    },
    {
        "transcript": """<customer>: Hi, I need help tracking my order. It hasn’t arrived yet.
                          <agent>: I’m sorry for the inconvenience. Can you provide your order number?
                          <customer>: It’s 78432.
                          <agent>: Thank you. I see the package is delayed due to weather. It should arrive within two days.
                          <customer>: Alright, I’ll wait. Thanks for the update.
                          <agent>: You’re welcome. Let me know if there’s anything else I can help with.""",
        "topics": ["1", "5"],
        "summary": "The customer called about a delayed package. The agent confirmed the delay was due to weather and provided a new delivery timeline."
    },
    {
        "transcript": """<customer>: Hi, I accidentally ordered two of the same dress. Can I return one?
                          <agent>: Of course. Would you like a refund or an exchange for a different item?
                          <customer>: A refund, please.
                          <agent>: Sure. I’ll email you a return label, and the refund will be processed upon receipt of the item.
                          <customer>: That works perfectly. Thanks!
                          <agent>: Anytime!""",
        "topics": ["2", "6"],
        "summary": "The customer accidentally ordered duplicate items and requested a refund for one. The agent provided a return label and initiated the refund process."
    },
    {
        "transcript": """<customer>: Hi, I noticed a tear in the dress I just received.
                          <agent>: I’m sorry to hear that. Would you like a replacement or a refund?
                          <customer>: A replacement, please.
                          <agent>: I’ll process that for you. The new dress will be shipped today and should arrive in 3-5 days.
                          <customer>: Thank you for resolving this quickly.
                          <agent>: You’re welcome!""",
        "topics": ["2", "8"],
        "summary": "The customer received a damaged dress and requested a replacement. The agent processed the replacement and provided a delivery timeline."
    },
    {
        "transcript": """<customer>: Hi, I’m looking for outfit recommendations for a summer wedding.
                          <agent>: Sure! Are you looking for something formal or semi-formal?
                          <customer>: Semi-formal, preferably light colors.
                          <agent>: I recommend checking out our summer collection. I’ll email you some options.
                          <customer>: That sounds great. Thanks!
                          <agent>: You’re welcome!""",
        "topics": ["10"],
        "summary": "The customer sought styling advice for a summer wedding. The agent suggested items from the summer collection and offered to send recommendations via email."
    },
    {
        "transcript": """<customer>: Hi, I think I left an item in my cart, but I can’t find it anymore.
                          <agent>: Let me check your account. Can you confirm your email address?
                          <customer>: Sure, it’s user123@example.com.
                          <agent>: Thank you. I see the item in your saved cart. Would you like me to place the order for you?
                          <customer>: Yes, please.
                          <agent>: Done! You’ll receive a confirmation email shortly.
                          <customer>: Thank you so much!
                          <agent>: My pleasure!""",
        "topics": ["7"],
        "summary": "The customer couldn’t find an item they left in their cart. The agent retrieved the item and completed the order on their behalf."
    },
    {
        "transcript": """<customer>: Hi, I received the wrong item in my order. I ordered a jacket, but I got a sweater.
                          <agent>: I apologize for the mistake. Would you like us to send the correct item or issue a refund?
                          <customer>: I’d like the correct item, please.
                          <agent>: I’ll arrange for the jacket to be shipped. Please use the return label I’ll email you to send the sweater back.
                          <customer>: Got it. Thank you!
                          <agent>: You’re welcome!""",
        "topics": ["2", "8"],
        "summary": "The customer received the wrong item in their order. The agent arranged for the correct item to be shipped and provided a return label for the incorrect one."
    },
    {
        "transcript": """<customer>: Hi, I’m wondering if your site has any size charts for dresses.
                          <agent>: Yes, we do. I’ll email you a link to our size chart for dresses.
                          <customer>: That would be great. Thank you!
                          <agent>: Happy to help! Let me know if there’s anything else.""",
        "topics": ["3"],
        "summary": "The customer requested a size chart for dresses. The agent provided a link to the chart to assist with sizing decisions."
    },
    {
        "transcript": """<customer>: Hi, I’m trying to place an order, but my payment keeps getting declined.
                          <agent>: I’m sorry to hear that. Have you checked with your bank about any restrictions?
                          <customer>: Yes, they said everything is fine on their end.
                          <agent>: Let me check your account. It seems there’s a technical error. I’ll escalate this to our IT team.
                          <customer>: Thanks. Will I be notified when it’s fixed?
                          <agent>: Absolutely. You’ll receive an email as soon as the issue is resolved.""",
        "topics": ["6", "7"],
        "summary": "The customer experienced payment issues while placing an order. The agent identified a technical error and escalated it to the IT team for resolution."
    },
{
        "transcript": """<customer>: Hi, I ordered a sweater, but the material feels different from the description online.
                          <agent>: I’m sorry to hear that. Would you like to return it for a refund or exchange it for something else?
                          <customer>: I’d like a refund, please.
                          <agent>: I’ll email you a return label. Once we receive the item, the refund will be processed within 3-5 business days.
                          <customer>: Thank you.
                          <agent>: You’re welcome.""",
        "topics": ["2", "8"],
        "summary": "The customer returned a sweater due to a material discrepancy. The agent provided a return label and explained the refund process."
    },
    {
        "transcript": """<customer>: Hello, I saw an email about a flash sale, but I’m not sure if it’s still active.
                          <agent>: Let me check for you. Can you confirm the code mentioned in the email?
                          <customer>: Yes, it’s FLASH20.
                          <agent>: The sale is active until midnight tonight. You can use the code at checkout to get 20% off.
                          <customer>: That’s great! Thanks for confirming.
                          <agent>: Happy to help!""",
        "topics": ["5"],
        "summary": "The customer inquired about a flash sale. The agent confirmed the sale details and provided instructions for applying the discount code."
    },
    {
        "transcript": """<customer>: Hi, I ordered a dress for an event tomorrow, but it hasn’t arrived yet.
                          <agent>: I’m sorry to hear that. Can you provide your order number?
                          <customer>: It’s 98765.
                          <agent>: Thank you. I see there’s a shipping delay. I’ll arrange for expedited delivery to ensure it arrives tomorrow morning.
                          <customer>: That’s perfect. Thank you!
                          <agent>: My pleasure!""",
        "topics": ["1", "5"],
        "summary": "The customer called about a delayed dress order for an upcoming event. The agent arranged expedited delivery to ensure timely arrival."
    },
    {
        "transcript": """<customer>: Hi, I want to exchange a pair of jeans for a smaller size.
                          <agent>: Sure! Can you provide your order number and the new size you need?
                          <customer>: My order number is 12345, and I need a size 28 instead of 30.
                          <agent>: Thank you. I’ll email you a return label, and we’ll send the smaller size upon receipt.
                          <customer>: Thanks for your help.
                          <agent>: You’re welcome!""",
        "topics": ["2", "3"],
        "summary": "The customer requested an exchange for a smaller size of jeans. The agent provided a return label and arranged for the exchange."
    },
    {
        "transcript": """<customer>: Hi, I’m locked out of my account and can’t reset my password.
                          <agent>: I’m sorry to hear that. Can I verify your email address to assist you?
                          <customer>: Sure, it’s user@example.com.
                          <agent>: Thank you. I’ve reset your account. You’ll receive an email shortly with a link to set a new password.
                          <customer>: Perfect, thank you!
                          <agent>: Happy to help.""",
        "topics": ["7"],
        "summary": "The customer was locked out of their account and unable to reset their password. The agent resolved the issue and provided instructions to set a new password."
    },
    {
        "transcript": """<customer>: Hello, do you offer gift wrapping for online orders?
                          <agent>: Yes, we do! You can select the gift-wrapping option at checkout for a small fee.
                          <customer>: Great! I’ll do that for my next order. Thanks for the info.
                          <agent>: You’re welcome. Let us know if you have more questions.""",
        "topics": [],
        "summary": "The customer inquired about gift-wrapping services. The agent provided details about the option and how to apply it at checkout."
    },
    {
        "transcript": """<customer>: Hi, I received my shoes, but they’re slightly damaged.
                          <agent>: I’m sorry to hear that. Would you like a replacement or a refund?
                          <customer>: A replacement, please.
                          <agent>: Can I have your order number?
                          <customer>: It’s 67890.
                          <agent>: Thank you. The replacement will be shipped immediately and should arrive in 3-5 business days.
                          <customer>: Thank you for resolving this quickly.
                          <agent>: Anytime!""",
        "topics": ["2", "8"],
        "summary": "The customer received damaged shoes and requested a replacement. The agent processed the replacement and ensured expedited shipping."
    },
    {
        "transcript": """<customer>: Hi, I need help choosing a blazer for a work presentation.
                          <agent>: Of course! Do you have a preferred style or color in mind?
                          <customer>: Something classic, maybe navy blue or black.
                          <agent>: I recommend our tailored-fit navy blazer. I can email you more options as well.
                          <customer>: That sounds great. Thank you!
                          <agent>: You’re welcome!""",
        "topics": ["10"],
        "summary": "The customer sought styling advice for a work presentation. The agent recommended a navy blazer and offered additional options via email."
    },
    {
        "transcript": """<customer>: Hi, I noticed a $15 charge on my card that I don’t recognize.
                          <agent>: I’m sorry for the inconvenience. Can you provide the transaction date?
                          <customer>: It’s from last week.
                          <agent>: I see it was a system error. I’ve initiated a refund, and it should reflect in your account within 3-5 business days.
                          <customer>: Thank you for resolving this quickly.
                          <agent>: You’re welcome!""",
        "topics": ["6"],
        "summary": "The customer reported an unrecognized charge. The agent confirmed it was a system error and processed a refund."
    },
    {
        "transcript": """<customer>: Hi, I ordered a handbag as a gift, but I selected the wrong color.
                          <agent>: I’m sorry to hear that. Would you like to exchange it for the correct color?
                          <customer>: Yes, please. I’d like the red one instead of black.
                          <agent>: I’ll arrange that for you. You’ll receive a return label to send back the black one, and the red handbag will be shipped.
                          <customer>: That’s perfect. Thank you!
                          <agent>: Anytime!""",
        "topics": ["2"],
        "summary": "The customer ordered the wrong color handbag and requested an exchange. The agent arranged the exchange and provided a return label for the incorrect item."
    }
]


class Command(BaseCommand):
    help = "Creates a sample set of data to test the app. Meant to be run locally."

    def handle(self, *args, **options):
        try:
            self.stdout.write('Creating Sample Organizations')
            org = Organization(name='ACME Org', max_user_count=20)
            org.save()

            other_org = Organization(name='Competitors Inc.')
            other_org.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Organizations: {e}')

        try:
            self.stdout.write('Creating 10 Sample Topics for ACME Org')

            topics = []
            for data in TOPIC_DATA:
                topic = Topic(
                    name=data["name"],
                    description=data["description"],
                    organization=org
                )
                topic.save()
                topics.append(topic)

            self.stdout.write('Successfully created 10 Sample Topics for ACME Org')

        except Exception as e:
            raise CommandError(f'Failed creation of Sample Topics: {e}')

        try:
            self.stdout.write('Creating Organization Admin')
            user = User.objects.create_user(
                email='org_admin@acme.org',
                auth_type='password',
                first_name='Org Admin',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD,
            )

            analyst = Analyst(
                organization=org,
                user=user,
                is_organization_admin=True,
            )
            analyst.save()

        except Exception as e:
            raise CommandError(f'Failed creation of Organization Admin: {e}')

        try:
            self.stdout.write('Creating Sample Analysts')
            user = User.objects.create_user(
                email='analyst_01@acme.org',
                auth_type='password',
                first_name='Analyst 1',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            analyst = Analyst(
                organization=org,
                user=user,
                is_organization_admin=False,
            )
            analyst.save()

            user = User.objects.create_user(
                email='analyst_01@competitors.inc',
                auth_type='password',
                first_name='Analyst 1',
                last_name='Competitors'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            competitor_analyst = Analyst(
                organization=other_org,
                user=user
            )
            competitor_analyst.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Analysts: {e}')

        try:
            self.stdout.write('Creating 15 Sample Agents under manager_01')
            user = User.objects.create_user(
                email='manager_01@acme.org',
                auth_type='password',
                first_name='Manager 1',
                last_name='Acme'
            )
            auth.update_user(
                user.id,
                email_verified=True,
                password=COMMON_PASSWORD
            )

            manager = Agent(
                organization=org,
                user=user,
                is_organization_admin=False,
            )
            manager.save()

            agents = []
            for i in range(1, 17):  # Creating agent_02 to agent_16
                user = User.objects.create_user(
                    email=f'agent_{i:02d}@acme.org',
                    auth_type='password',
                    first_name=f'Agent {i}',
                    last_name='Acme'
                )
                auth.update_user(
                    user.id,
                    email_verified=True,
                    password=COMMON_PASSWORD
                )

                agent = Agent(
                    organization=org,
                    user=user,
                    manager=manager
                )
                agent.save()
                agents.append(agent)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Agents: {e}')

        try:
            self.stdout.write('Creating 50 Sample Customers for ACME Org')
            customers = []
            for i in range(50):
                customer = Customer(
                    external_id=hashlib.sha256(f'{i + 1}{int(time.time())}'.encode()).hexdigest(),
                    organization=org
                )
                customer.save()
                customers.append(customer)
        except Exception as e:
            raise CommandError(f'Failed creation of Sample Customers: {e}')

        try:
            self.stdout.write('Creating 50 Sample Conversations for ACME Org Customers')
            base_date = datetime.now() - timedelta(days=90)
            for i, data in enumerate(CONVERSATION_DATA):
                agent = random.choice(agents)
                customer = random.choice(customers)
                naive_date = base_date + timedelta(days=random.randint(0, 90))  # Naive datetime
                date = timezone.make_aware(naive_date)  # Convert to aware datetime
                sentiment = random.uniform(0, 5)  # Sentiment between 0 and 5
                duration = random.randint(30, 1800)  # Random duration in seconds

                conversation = Conversation(
                    path=f'/random/path/{i}',
                    date=date,
                    duration=duration,
                    transcript=data['transcript'],
                    sentiment=sentiment,
                    title=f"Conversation {i + 1} - {agent.user.email} assists {customer.external_id}",
                    summary=data['summary'],
                    input_tokens=random.randint(50, 200),
                    output_tokens=random.randint(20, 100),
                    customer=customer,
                    agent=agent
                )
                conversation.save()

                # Assign random topics
                conversation.topics.add(*data['topics'])
                conversation.save()
        except Exception as e:
            raise CommandError(f'Failed creation of Conversations: {e}')

        try:
            self.stdout.write('Setting the last 2 Sample Topics as Inactive')
            time.sleep(1)
            for i in range(8, 10):
                topic = Topic.objects.get(name=TOPIC_DATA[i]['name'], organization=org)
                topic.is_active = False
                topic.save()
        except Exception as e:
            raise CommandError(f'Failed setting topics to inactive: {e}')

        try:
            self.stdout.write('Creating Superuser')
            user = User.objects.create_superuser(
                email='altogi@tellme.ch',
                password=COMMON_PASSWORD,
                first_name='Alvaro',
                last_name='Tomas Gil'
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser: {e}')

        try:
            self.stdout.write('Creating Superuser Account for Invoking Processing Pipeline')
            user = User.objects.create_superuser(
                email=settings.PROCESSING_PIPELINE_USER,
                password=COMMON_PASSWORD,
                first_name='Processing',
                last_name=settings.TELLME_ENV
            )
            auth.update_user(
                user.id,
                email_verified=True
            )
        except Exception as e:
            raise CommandError(f'Failed to create Superuser: {e}')

        try:
            self.stdout.write('Creating Organization API Key for Processing')
            plain_key = OrganizationAPIKey.create_key(org, name='test_key')
            self.stdout.write(f'Created API Key for {org.name}: {plain_key}')
        except Exception as e:
            raise CommandError(f'Failed to create Organization API Key: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created expanded sample data')
        )
