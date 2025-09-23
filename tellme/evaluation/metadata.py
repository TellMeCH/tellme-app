

TOPICS = [
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
    }
]

SUGGESTED_TOPICS = [    
    {
        "name": "Discounts and Promotions",
        "description": "Inquiries about current or upcoming sales, discount codes, loyalty rewards, and special offers."
    },
    {
        "name": "Payments, Refunds, and Billing",
        "description": "Issues or questions about payment methods, billing discrepancies, refunds or installment plans."
    }
]

CONVERSATIONS = [
    {
        "input": {
            "file_name": "pkz_1.wav",
            "organization_id": "1",
            "customer_id": "1",
            "agent_id": "1",
            "timestamp": "2025-09-22T08:25:00+02:00"
        },
        "output": {
            "customer_id": "PeterMeier15/07/1981",
            "topics": ["Returns and Exchanges"],
            "suggested_topics": ["Payments, Refunds, and Billing"],
            "new_topics": [
                {"name": "Agent Misconduct",
                 "description": "Customer complaints regarding inappropriate or unhelpful behavior by a support agent, including rudeness, dismissiveness, or lack of professionalism during interactions."}],
            "transcript":
                """
                <agent>: PKZ Customer Service. How can I help you?
                <customer>: Hi, I placed an order for a pair of men's sandals, but you sent me the women's version by mistake.
                <agent>: Are you sure you ordered the men's sandals? Sometimes customers select the wrong item by accident.
                <customer>: Of course I'm sure. I double-checked my order confirmation email. Can you check your system and get me the right product?
                <agent>: I suppose. What's your name and birthdate?
                <customer>: Peter Meier, July 15th, 1981.
                <agent>: Fine, wait a second... (pause) Well, I see the order here, but honestly, sending the wrong item can happen. You can just return them if you want.
                <customer>: That's not helpful. I need them for my vacation soon. Can you arrange a replacement or at least speed up the process?
                <agent>: Look, our policy is clear: you need to return the product first. Once we get it, we’ll decide if you get a refund or not.
                <customer>: That’s really not acceptable. It was your mistake.
                <agent>: Sir, mistakes happen. I’m just telling you what the rules are. I can’t help if you don’t want to cooperate.
                <customer>: This is unbelievable. I’m going to report your attitude to your supervisor. This is not how you treat customers!
                <agent>: You can do whatever you want, sir. That’s our policy.
                <customer>: I’ll be sure to let others know about this experience. Goodbye.
                <agent>: Goodbye.
                """,
            "sentiment": "1",
            "summary": "The customer called to report that he had received women's sandals instead of the men's sandals he ordered. He asked for assistance in getting the correct item sent before an upcoming vacation. The agent was dismissive and did not offer meaningful help, insisting on the standard returns procedure and displaying poor customer service. The conversation became heated, with the customer expressing strong dissatisfaction and threatening to report the agent's conduct. Topics discussed include returns and exchanges, as well as a new topic: agent misconduct. The interaction ended without resolution, and the customer's impression of the company was negative.",
            "title": "Order Issue Escalates to Agent Misconduct Complaint",
            "revenue_search_query": "pkz men sandals",
            "revenue": "162.4"
        }
    },
    {
        "input": {
            "file_name": "pkz_2.wav",
            "organization_id": "1",
            "customer_id": "2",
            "agent_id": "2",
            "timestamp": "2025-09-22T08:27:00+02:00"
        },
        "output": {
            "customer_id": "AnnaKeller03/03/1992",
            "topics": ["Sizing and Fit"],
            "suggested_topics": [],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Customer Service, how may I assist you today?
                <customer>: Hello! I’m interested in purchasing your blue sundress, but I’m unsure about the sizing. Could you help me figure out which size would fit me best?
                <agent>: Absolutely, I’d be happy to help! May I have your name and birthdate first, just to keep our records up to date?
                <customer>: Sure! Anna Keller, born March 3rd, 1992.
                <agent>: Thank you, Anna. Now, may I ask for your usual dress size or any specific measurements? That will help me suggest the best fit.
                <customer>: I usually wear a size 38 in most brands, but sometimes size charts can vary a bit. My bust is 92 cm and my waist is 74 cm.
                <agent>: Perfect, thank you! For the blue sundress, our size 38 is designed for a bust between 90-94 cm and a waist of 72-76 cm, which sounds like a very good match for you. The fit is slightly relaxed, so it shouldn’t feel too tight.
                <customer>: That’s great to hear! I was worried it might be too snug, but if it’s a relaxed fit, size 38 sounds ideal. Do you have any advice if I’m between sizes?
                <agent>: If you prefer a looser look, you could size up to a 40, but based on your measurements and preferences, 38 should be flattering and comfortable. All dresses also have a 30-day return policy in case you need to exchange.
                <customer>: Wonderful, thank you so much for your help! You’ve made my decision really easy.
                <agent>: My pleasure, Anna. If you have any more questions before you order, just give us a call. Have a lovely day!
                <customer>: Thanks again, you too!
                <agent>: Goodbye!
                """,
            "sentiment": "5",
            "summary": "The customer called PKZ Customer Service to inquire about the sizing of a blue sundress she wished to purchase. After providing her name, birthdate, and measurements, the agent gave her clear guidance on which size would be ideal based on the product's fit and measurements. The agent also mentioned the return policy for added reassurance. The conversation was friendly and helpful throughout, leaving Anna satisfied and confident in her purchase decision. No additional topics outside sizing and fit were discussed.",
            "title": "Assistance with Sundress Sizing Provided Cordially",
            "revenue_search_query": "pkz woman dress",
            "revenue": "472.06"
        }
    },
    {
        "input": {
            "file_name": "pkz_3.wav",
            "organization_id": "1",
            "customer_id": "3",
            "agent_id": "3",
            "timestamp": "2025-09-22T08:40:00+02:00"
        },
        "output": {
            "customer_id": None,
            "topics": ["Product Availability"],
            "suggested_topics": [],
            "new_topics": [{"name": "Product Materials",
                            "description": "Questions and information requests regarding the materials a product is made from, with a focus on aspects such as sustainability, origin, and quality."}],
            "transcript":
                """
                <agent>: PKZ Kundenservice, wie kann ich Ihnen helfen?
                <customer>: Guten Tag, ich wollte fragen, ob der blaue Wollpullover in Größe L noch verfügbar ist.
                <agent>: Lassen Sie mich einen Moment nachschauen… Der Pullover war leider sehr stark nachgefragt und ist aktuell ausverkauft. Aber wir erwarten, dass wir ihn Ende des Monats wieder auf Lager haben.
                <customer>: Könnten Sie mir vielleicht eine E-Mail schicken, sobald der Pullover wieder verfügbar ist?
                <agent>: Das lässt sich einrichten. Ich notiere Ihre Anfrage und informiere Sie per E-Mail, sobald der Artikel zurück ist.
                <customer>: Super, danke. Können Sie mir noch sagen, aus welchem Material der Pullover gemacht ist und ob er nachhaltig gefertigt wurde?
                <agent>: Natürlich. Der Pullover besteht zu 100% aus Bio-Merino-Wolle. Unser Lieferant ist GOTS-zertifiziert, was für faire Bedingungen und nachhaltige Produktion steht.
                <customer>: Danke für die ausführliche Info.
                <agent>: Sehr gern. Ich melde mich, sobald der Pullover wieder verfügbar ist. Gibt es sonst noch etwas, womit ich helfen kann?
                <customer>: Nein, das war’s. Vielen Dank und einen schönen Tag noch.
                <agent>: Ihnen auch, auf Wiederhören!
                """,
            "sentiment": "3",
            "summary": "The customer called to inquire about the availability of a specific blue wool sweater in size L. The agent informed him that it is currently sold out but will be restocked at the end of the month and offered to send an email notification once available. Markus also asked for details about the material and sustainability of the sweater and was reassured that it is made from organic merino wool with GOTS certification. The conversation was neutral and efficient, covering product availability and material information.",
            "title": "Inquiry on Sweater Availability & Material Details",
            "revenue_search_query": "pkz men pullover",
            "revenue": "282.36"
        }
    },
    {
        "input": {
            "file_name": "pkz_4.wav",
            "organization_id": "1",
            "customer_id": "4",
            "agent_id": "4",
            "timestamp": "2025-09-22T08:46:00+02:00"
        },
        "output": {
            "customer_id": "SabineMüller30/08/1975",
            "topics": [],
            "suggested_topics": ["Discounts and Promotions"],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Kundenservice, was kann ich für Sie tun?
                <customer>: Guten Morgen. Können Sie mir sagen, wann die nächste Sale-Saison beginnt?
                <agent>: Sehr gern! Könnten Sie mir bitte zuerst Ihren Namen und Ihr Geburtsdatum nennen?
                <customer>: Sabine Müller, 30. August 1975.
                <agent>: Vielen Dank, Frau Müller. Die nächste Sale-Saison startet offiziell am 1. Oktober.
                <customer>: Betrifft das Angebot auch die Schmuckabteilung?
                <agent>: Ja, bei den meisten Aktionen sind auch viele Schmuckartikel dabei. Details zu den Marken geben wir Ende September bekannt.
                <customer>: Gibt es denn schon Infos, welche Marken teilnehmen werden?
                <agent>: Noch nicht im Detail, aber basierend auf den Vorjahren werden Marken wie Swarovski und Thomas Sabo dabei sein. Die finale Liste folgt mit dem Start der Aktion.
                <customer>: Und wie hoch werden die Rabatte ungefähr sein?
                <agent>: Das ist unterschiedlich, aber normalerweise gibt es auf Schmuck zwischen 20% und 40% Rabatt, je nach Marke und Produkt.
                <customer>: Sind alle Schmuckstücke im Sale, oder nur bestimmte?
                <agent>: Im Regelfall sind vor allem saisonale Kollektionen reduziert. Einzelne exklusive Stücke können ausgeschlossen sein, aber genaue Infos gibt’s zum Start der Aktion online und im Geschäft.
                <customer>: Wann sollte ich am besten nachsehen?
                <agent>: Ab 1. Oktober finden Sie alle Rabatte und Markenübersichten auf unserer Website und direkt in unseren Filialen.
                <customer>: Vielen Dank, ich wollte einfach ganz sicher gehen.
                <agent>: Kein Problem, gerne geschehen. Haben Sie sonst noch eine Frage?
                <customer>: Nein, das wäre alles. Vielen Dank für Ihre Geduld!
                <agent>: Sehr gerne, Frau Müller. Ich wünsche Ihnen einen schönen Tag!
                """,
            "sentiment": "5",
            "summary": "The customer called to inquire about the next sale season and whether it would include the jewelry department. She repeatedly asked about the sale dates, participating brands, and potential discount rates. The agent answered each query patiently and provided details about the upcoming sale, expected brands, and typical discount ranges for jewelry. The conversation was friendly and the agent remained polite and helpful throughout.",
            "title": "Detailed Discount Inquiry with Jewelry Focus",
            "revenue_search_query": "pkz women schmuck",
            "revenue": "84.90"
        }
    },
    {
        "input": {
            "file_name": "pkz_5.wav",
            "organization_id": "1",
            "customer_id": "5",
            "agent_id": "5",
            "timestamp": "2025-09-22T09:07:00+02:00"
        },
        "output": {
            "customer_id": "GregorWeiss18/12/1984",
            "topics": ["Order Status"],
            "suggested_topics": ["Payments, Refunds, and Billing"],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Customer Service, how may I help you?
                <customer>: Yes, I ordered a suit from your online store four days ago. I received an order confirmation but have heard nothing from your delivery company. What’s going on?
                <agent>: May I have your name and birthdate, please?
                <customer>: Gregor Weiss, December 18th, 1984.
                <agent>: Thank you, Mr. Weiss. Let me check your order… Alright, I see your order, but it appears there was an issue processing your payment.
                <customer>: That can't be. I paid with bitcoin because you finally accept it. How is there a problem?
                <agent>: We recently switched to a new payment provider that enables bitcoin payments. Unfortunately, there have been some integration issues, and your payment has not been fully received on our end.
                <customer>: Incredible. I paid in full on my side—how can this be my fault?
                <agent>: I'm not saying it's your fault, sir. We are currently working to resolve some technical difficulties with our new system.
                <customer>: Well, this is very inconvenient. I expected better from your company. I want my order processed immediately—or my bitcoin back.
                <agent>: I understand your frustration. I will escalate your case and make sure you receive an update on the status of your order by the end of the day.
                <customer>: You better. This is quite unprofessional.
                <agent>: Thank you for your patience. We'll be in touch as soon as we have an update.
                <customer>: Good.
                <agent>: Have a good day.
                """,
            "sentiment": "1",
            "summary": "The customer called to inquire about the status of his suit order, having received only an order confirmation and no delivery updates. The agent discovered a payment issue linked to bitcoin, resulting from a recent switch to a new payment provider and related technical problems. The customer was impatient and critical, expressing dissatisfaction with the process. The agent promised to escalate the issue and provide an update by the end of the day. Main topics discussed were order status and payment processing. The overall engagement was low.",
            "title": "Order Status Problem Due to Bitcoin Payment Integration",
            "revenue_search_query": "pkz men suits",
            "revenue": "714.90"
        }
    },
    {
        "input": {
            "file_name": "pkz_6.wav",
            "organization_id": "1",
            "customer_id": "6",
            "agent_id": "6",
            "timestamp": "2025-09-22T09:13:00+02:00"
        },
        "output": {
            "customer_id": "ClaudiaSchulz12/05/1990",
            "topics": ["Returns and Exchanges"],
            "suggested_topics": ["Payments, Refunds, and Billing"],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Kundenservice, wie kann ich Ihnen helfen?
                <customer>: Hallo, ich habe vor einer Woche ein Paar High Heel Schuhe zurückgeschickt und wollte wissen, ob die Retoure schon angekommen ist.
                <agent>: Natürlich, könnten Sie mir bitte Ihren Namen und Ihr Geburtsdatum nennen?
                <customer>: Ja, Claudia Schulz, 12. Mai 1990.
                <agent>: Vielen Dank, Frau Schulz. Einen Moment bitte, ich prüfe das für Sie... Laut unserem System haben wir gestern eine Postbenachrichtigung erhalten, dass das Paket unterwegs ist. Sobald es bei uns eingeht, bekommen Sie eine Bestätigung per E-Mail.
                <customer>: Gut, danke. Wie lange dauert es normalerweise, bis das Geld wieder auf meinem Konto ist?
                <agent>: In der Regel erfolgt die Rückerstattung innerhalb von fünf Werktagen nach Eingang des Artikels bei uns. Sie erhalten dann automatisch alle weiteren Informationen per E-Mail.
                <customer>: Alles klar, danke für die Auskunft.
                <agent>: Sehr gern! Kann ich sonst noch etwas für Sie tun?
                <customer>: Nein, das war’s. Vielen Dank und schönen Tag!
                <agent>: Danke ebenso, Frau Schulz. Auf Wiederhören!
                """,
            "sentiment": "4",
            "summary": "The customer called to inquire about the status of her return for a pair of high heel shoes. The agent confirmed a postal notification showing the package is currently en route. Claudia then asked about the refund timeline, and the agent explained it typically takes five business days after the item is received. The interaction was polite and informative, focusing on returns and exchanges and touching on refund payment timing.",
            "title": "Return Status and Refund Timeline for High Heels",
            "revenue_search_query": "pkz high heels",
            "revenue": "185.90"
        }
    },
    {
        "input": {
            "file_name": "pkz_7.wav",
            "organization_id": "1",
            "customer_id": "7",
            "agent_id": "7",
            "timestamp": "2025-09-22T09:18:00+02:00"
        },
        "output": {
            "customer_id": None,
            "topics": ["Returns and Exchanges"],
            "suggested_topics": ["Product Materials"],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Kundenservice, wie darf ich Ihnen helfen?
                <customer>: Guten Tag. Ich interessiere mich für eine Ledertasche aus Ihrem Sortiment. Können Sie mir sagen, ob sie bei Ihren Kunden beliebt ist?
                <agent>: Sehr gerne! Die besagte Tasche gehört tatsächlich zu unseren meistverkauften Modellen und erhält regelmäßig positive Bewertungen von unseren Kunden.
                <customer>: Das klingt gut. Wissen Sie, aus welchem Material die Tasche genau gefertigt ist und wie die Qualität einzuschätzen ist?
                <agent>: Die Tasche besteht aus hochwertigem, vegetabil gegerbtem Echtleder, das sich durch besondere Langlebigkeit und Nachhaltigkeit auszeichnet. Die Verarbeitung ist sehr hochwertig, und das Leder stammt aus zertifizierten europäischen Gerbereien.
                <customer>: Sehr gut zu wissen. Und wie sieht es mit der Rückgabe aus, falls sie meiner Partnerin doch nicht gefällt?
                <agent>: Sie haben ein 30-tägiges Rückgaberecht ab dem Kaufdatum. Die Rückgabe kann unkompliziert in all unseren Filialen oder per Post erfolgen, sofern die Tasche unbenutzt ist.
                <customer>: Perfekt, vielen Dank für die Infos!
                <agent>: Sehr gern. Haben Sie sonst noch Fragen?
                <customer>: Nein, das war’s. Einen schönen Tag noch!
                <agent>: Ihnen auch, auf Wiederhören!
                """,
            "sentiment": "5",
            "summary": "The customer called to ask about a leather purse he was considering as a present for his partner. He inquired about customer popularity, material quality, and the return policy. The agent confirmed that the purse is highly rated, made of high-quality vegetable-tanned leather, and can be returned within 30 days if unused. The call was friendly and informative, with the primary topics being product materials and returns.",
            "title": "Customer Inquiry: Leather Purse Quality, Popularity & Return Policy",
            "revenue_search_query": "pkz taschen",
            "revenue": "453.80"
        }
    },
    {
        "input": {
            "file_name": "pkz_8.wav",
            "organization_id": "1",
            "customer_id": "8",
            "agent_id": "8",
            "timestamp": "2025-09-22T09:25:00+02:00"
        },
        "output": {
            "customer_id": "EmilyClark28/02/1993",
            "topics": ["Sizing and Fit", "Product Availability", "Returns and Exchanges"],
            "suggested_topics": [],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Customer Service, how may I assist you today?
                <customer>: Hi, I returned the jeans I ordered because they were way too small. I need a size L, but I see you only have M in stock and now nothing else. This is so frustrating.
                <agent>: I'm sorry to hear that. May I have your name and birthdate to look up your order?
                <customer>: Emily Clark, February 28th, 1993.
                <agent>: Thank you, Emily. I've found your order and can confirm we've received your return. Unfortunately, you're right—size L is out of stock at the moment.
                <customer>: That's really disappointing. I needed those jeans for an event next week. Why didn't you restock more sizes?
                <agent>: I understand it's frustrating, and I apologize for the inconvenience. Right now, we don't have an estimated restock date for the L, but I can process a refund for the returned jeans. Would you like to be notified by email as soon as the L is back in stock?
                <customer>: I guess I have no choice, do I? Yes, go ahead and refund me and please let me know if they’re restocked.
                <agent>: Absolutely. I'll start the refund process right away and make a note to send you an email notification once size L becomes available again.
                <customer>: Alright, thanks.
                <agent>: You're welcome, Emily. Let us know if there's anything else we can do.
                <customer>: That's all. Bye.
                <agent>: Goodbye.
                """,
            "sentiment": "2",
            "summary": "The customer called about returning a pair of jeans that were too small and found that her required size L was not in stock. She expressed frustration over the sizing issue and the product's unavailability. The agent apologized and offered a refund along with an email notification when the product is restocked. Emily agreed to the refund and notification. The call focused on sizing and fit, product availability, and returns.",
            "title": "Unhappy Customer: Jeans Size Issue and Out-of-Stock Situation",
            "revenue_search_query": "pkz women jeans",
            "revenue": "177.99"
        }
    },
    {
        "input": {
            "file_name": "pkz_9.wav",
            "organization_id": "1",
            "customer_id": "9",
            "agent_id": "9",
            "timestamp": "2025-09-22T09:29:00+02:00"
        },
        "output": {
            "customer_id": None,
            "topics": [],
            "suggested_topics": [],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Kundenservice, wie kann ich Ihnen weiterhelfen?
                <customer>: Guten Morgen! Ich hätte gern zwei Kilo Rippchen bestellt, bitte.
                <agent>: Entschuldigen Sie, aber hier ist PKZ Kundenservice für Kleidung und Mode. Sie haben vermutlich eine falsche Nummer gewählt.
                <customer>: Oh, ist das nicht die Metzgerei Klaus?
                <agent>: Nein, tut mir leid, das ist eine Modefirma. Die Metzgerei hat sicher eine andere Nummer.
                <customer>: Das ist jetzt aber peinlich. Entschuldigung!
                <agent>: Kein Problem, das passiert öfter als man denkt. Ich wünsche Ihnen trotzdem viel Erfolg beim Metzger!
                <customer>: Dankeschön und einen schönen Tag!
                <agent>: Ihnen auch, auf Wiederhören!
                """,
            "sentiment": "5",
            "summary": "A caller mistakenly contacted PKZ Customer Service, thinking it was the local butcher. The agent clarified they were a clothing store, not a butcher shop. The caller apologized for the confusion, and the agent responded kindly. The call ended on a friendly note, with no business topics discussed.",
            "title": "Friendly Wrong Number Call",
            "revenue_search_query": None,
            "revenue": None
        }
    },
    {
        "input": {
            "file_name": "pkz_10.wav",
            "organization_id": "1",
            "customer_id": "10",
            "agent_id": "10",
            "timestamp": "2025-09-22T09:32:00+02:00"
        },
        "output": {
            "customer_id": "MichaelThompson06/06/1995",
            "topics": ["Order Status"],
            "suggested_topics": [],
            "new_topics": [],
            "transcript":
                """
                <agent>: PKZ Customer Service, how can I help you?
                <customer>: Hi, I recently ordered a pair of sneakers, but the courier hasn't been able to reach me for delivery. I think they have the wrong phone number.
                <agent>: I understand. To help, could you please tell me your name and date of birth?
                <customer>: Sure—Michael Thompson, June 6th, 1995.
                <agent>: Thank you, Michael. Let me look into your order… Yes, I see there have been two failed delivery attempts, and the contact number on file ends with 7832. Is that your current number?
                <customer>: No, that's my old number. My new number is 078 456 7890.
                <agent>: I've updated your delivery details with the correct phone number. The courier will now contact you on your new number for the next delivery attempt.
                <customer>: Great, thank you.
                <agent>: You're welcome. Please let us know if you need any further help.
                <customer>: Will do, thanks again. Goodbye.
                <agent>: Goodbye.
                """,
            "sentiment": "3",
            "summary": "The customer called to update the phone number associated with his delivery address after a pair of sneakers could not be delivered. The agent confirmed two failed delivery attempts due to the outdated number and updated the contact information as requested. The call was straightforward and focused on resolving the delivery issue, with a neutral tone throughout.",
            "title": "Order Delivery Issue Resolved with Updated Contact Information",
            "revenue_search_query": "pkz men sneakers",
            "revenue": "232.40"
        }
    }
]
