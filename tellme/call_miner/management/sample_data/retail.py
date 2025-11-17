"""
Sample data for retail demo
"""

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
SUGGESTED_TOPIC_DATA = [
    {
        "name": "Technical Support",
        "description": "Calls related to technical issues with products, troubleshooting, and software or hardware problems that customers encounter."
    },
    {
        "name": "Warranty Claims",
        "description": "Customer inquiries about warranty coverage, warranty claims, and requests for repairs or replacements under warranty terms."
    }
]
CONVERSATION_DATA = [
{
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe eine allgemeine Frage zu meinen Versicherungen bei der Vaudoise.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Womit kann ich Ihnen helfen?
<customer>: Ich habe so viele verschiedene Policen, dass ich langsam den Überblick verliere. Können Sie mir sagen, was aktuell alles bei mir versichert ist?
<agent>: Natürlich. Dann starte ich am besten einen Gesamtüberblick. Haben Sie bitte kurz Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 45-AN-1295-M8.
<agent>: Vielen Dank. Einen Moment… ich sehe hier eine Hausrat-, eine Fahrzeug- und eine Reiseversicherung. Dazu noch eine kleine Lebensversicherung.
<customer>: Und wie sieht es mit einer Rechtsschutzversicherung aus? Ich dachte, ich hätte eine.
<agent>: Ich sehe im System keinen aktiven Rechtsschutzvertrag. Wir könnten prüfen, ob das für Sie sinnvoll wäre.
<customer>: Hm, das überrascht mich. Ich war sicher, dass ich eine habe. Das ärgert mich gerade ein bisschen.
<agent>: Das verstehe ich gut. Wenn Sie möchten, kann ich Ihnen eine kurze Zusammenstellung inkl. Offerte für eine Rechtsschutzversicherung per E-Mail schicken.
<customer>: Ja, tun Sie das bitte. Aber ich entscheide danach in Ruhe. Keine automatische Aktivierung!
<agent>: Selbstverständlich, es handelt sich nur um eine unverbindliche Offerte. Ist die E-Mail-Adresse dvorak@gmail.com noch aktuell?
<customer>: Ja, die stimmt.
<agent>: Perfekt, dann erhalten Sie im Laufe des Tages eine Übersicht über Ihre bestehenden Policen und einen separaten Vorschlag für die Rechtsschutzversicherung.
<customer>: Gut, danke. Dann warte ich darauf.
<agent>: Sehr gerne, Frau Dvorak. Wenn danach noch Fragen offen sind, können Sie uns jederzeit wieder anrufen.""",
        "topics": ["1"],
        "summary": "Customer wants a complete overview of her existing insurance policies and discovers that no legal protection insurance is present. She receives an overview and a non-binding quote.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe das Gefühl, dass ich bei der Vaudoise nicht alles versichert habe, was ich eigentlich brauche.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Welche Situation beschäftigt Sie konkret?
<customer>: Wir haben kürzlich eine kleine Ferienwohnung gekauft, und mir ist aufgefallen, dass diese nirgends explizit erwähnt ist.
<agent>: Verstehe. Dann schauen wir uns Ihre Policen an. Könnten Sie mir bitte Ihre Kundennummer oder eine Policennummer geben?
<customer>: Die Policennummer ist UD-5715-K7.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung aktuell nur auf Ihre Hauptwohnung läuft. Die Ferienwohnung ist tatsächlich nicht eingeschlossen.
<customer>: Das ist genau das, was ich befürchtet habe. Wenn dort etwas passiert, stehe ich dann komplett ohne Schutz da?
<agent>: Für Schäden vor Ort, ja, aktuell wäre dort keine Deckung. Wir können das Objekt aber relativ einfach in Ihre Hausratversicherung integrieren oder separat versichern.
<customer>: Warum hat mir das niemand gesagt, als ich angerufen habe, bevor wir gekauft haben?
<agent>: Es tut mir leid, wenn das damals nicht klar kommuniziert wurde. Ich kann Ihren Fall intern vermerken, damit wir das überprüfen.
<customer>: Ich bin ehrlich gesagt ziemlich verärgert. Das ist doch Ihr Job, mich auf solche Lücken hinzuweisen.
<agent>: Ich verstehe Ihren Ärger sehr gut. Als Sofortmassnahme könnte ich Ihnen eine provisorische Deckung ab heute einrichten, damit Sie nicht länger ohne Schutz sind. Die definitive Police würden wir Ihnen dann schriftlich zustellen.
<customer>: Gut, dann machen Sie das bitte. Aber ich möchte keine versteckten Zusatzkosten.
<agent>: Selbstverständlich. Ich sende Ihnen noch heute eine transparente Offerte mit allen Prämien und Leistungen. Erst wenn Sie unterschreiben, wird die Police definitiv.
<customer>: In Ordnung, dann warte ich auf die Unterlagen. Wenn mir etwas komisch vorkommt, melde ich mich wieder.
<agent>: Das ist absolut in Ordnung. Vielen Dank für Ihre Offenheit, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer discovers that her new holiday apartment is not insured, is annoyed, and receives provisional coverage as well as a transparent quote to close the coverage gap.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Simic. I'm interested in additional insurance with Vaudoise.
<agent>: Good afternoon Mr. Simic, this is Nora Widmer. Nice that you're contacting us. What did you have in mind?
<customer>: I bought a new electric car and I'm wondering if I need something special for it.
<agent>: Congratulations on the new car! Do you drive the vehicle mainly privately or also for business?
<customer>: Only privately, but quite a lot. And I heard that batteries are very expensive if something happens to them.
<agent>: That's correct. We have a special module for electric vehicles that covers battery damage and extends assistance services.
<customer>: Sounds interesting. Can you give me an approximate idea of what this would cost me per year?
<agent>: If I base this on your current vehicle insurance with policy number VK-8002-K3, the additional module would be around 120 francs per year.
<customer>: Hmm. I honestly expected less.
<agent>: I understand. We could check whether you want optimizations on the deductible or other coverage to keep the overall premium stable.
<customer>: No, I don't want to tinker around everywhere. Just send me an offer, then I'll decide.
<agent>: Gladly. To which email address may I send the quote? I still have simic@gmail.com.
<customer>: Yes, that's correct. But please without automatic salutation "Dear Family", I hate that.
<agent>: Alright, I'll note that. You'll receive a personal quote addressed only to you.
<customer>: Good, then let's wait and see what comes.
<agent>: Very gladly, Mr. Simic. If you have questions afterwards or want to conclude directly, just contact us.""",
        "topics": ["3"],
        "summary": "Customer is interested in expanding his vehicle insurance for a new electric car. He has a quote sent to him but doesn't want any adjustments to other coverage for now.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. Il s'agit de mon sinistre en cours chez Vaudoise, et je ne suis pas satisfaite.
<agent>: Bonjour Madame Roth, ici Anna Meier. Je regrette d'apprendre que vous n'êtes pas satisfaite. De quel sinistre s'agit-il?
<customer>: Il s'agit des dégâts d'eau dans mon appartement, numéro de référence SV-5385-I9. Vous ne voulez me rembourser qu'une partie des coûts.
<agent>: Un moment, j'ouvre le dossier... Oui, je vois qu'une partie des coûts a été classée comme entretien non assuré.
<customer>: C'est exactement ce que je trouve injuste. J'ai tout fait entretenir régulièrement. Maintenant je me retrouve avec plusieurs milliers de francs à ma charge.
<agent>: Je comprends que ce soit frustrant. Selon l'expertise, les conduites étaient déjà fortement corrodées, ce qui constitue un défaut préexistant.
<customer>: Je ne peux pas accepter cela ainsi. Je n'ai jamais reçu d'écrit disant que quelque chose n'était pas en ordre.
<agent>: Ce que je peux faire pour vous: nous pouvons faire procéder à une seconde évaluation par un expert indépendant. Cela peut cependant prendre quelques jours.
<customer>: Franchement, j'en ai assez de ces "quelques jours". Cela traîne depuis des semaines.
<agent>: Je peux le comprendre. Alternativement, nous pourrions examiner un montant partiel comme paiement de complaisance, sans reconnaissance d'obligation légale.
<customer>: Alors, soit vous prenez en charge davantage, soit je vais voir l'ombudsman.
<agent>: Bien sûr, la voie vers l'ombudsman vous est ouverte. Je vous propose que j'escalade le dossier dès aujourd'hui à notre direction sinistres et que nous vous fassions parvenir une prise de position concrète au plus tard après-demain.
<customer>: Bien, faites cela. Mais si je reçois encore une réponse standard, vous ne me reverrez sûrement plus comme cliente.
<agent>: Je prends votre feedback très au sérieux et note votre plainte en détail dans le dossier.
<customer>: D'accord, alors j'attends maintenant UNE dernière fois votre retour.
<agent>: Merci pour votre patience, Madame Roth. Nous vous recontacterons le plus rapidement possible.""",
        "topics": ["4"],
        "summary": "Customer is dissatisfied with compensation after water damage. The case is escalated to claims management, a new review or possible goodwill solution is announced."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Steiner. Ich rufe wegen meines offenen Schadenfalls an. Ich habe seit zwei Wochen nichts mehr gehört.
<agent>: Guten Tag Frau Steiner, hier ist Sarah Dürst von der Vaudoise. Darf ich bitte die Schadenreferenz haben?
<customer>: Ja, das ist SN-2993-Z3.
<agent>: Vielen Dank. Ich schaue kurz nach… Ich sehe, dass wir noch auf eine Rückmeldung der Werkstatt warten, die die Reparaturkosten bestätigen soll.
<customer>: Das kann doch nicht Ihr Ernst sein. Ich habe das Auto vor zehn Tagen zurückbekommen.
<agent>: Es tut mir leid, dass das so lange dauert. Im System ist noch keine finale Rechnung hinterlegt.
<customer>: Ich habe die Rechnung gestern selber per E-Mail geschickt!
<agent>: Einen Moment… ah, ich sehe sie jetzt in unserem Posteingang, aber sie ist noch nicht im Dossier verbucht. Das hätte schneller passieren sollen, da gebe ich Ihnen recht.
<customer>: Ja, genau. Ich kann nicht ständig hinterhertelefonieren.
<agent>: Ich priorisiere Ihren Fall sofort und gebe ihn an die zuständige Schadensachbearbeiterin weiter. Sie erhalten spätestens morgen eine Bestätigung der Auszahlung.
<customer>: Versprechen Sie mir das? Ich habe schon einmal „morgen" gehört.
<agent>: Ich kann Ihnen zusagen, dass ich persönlich einen Reminder setze und Sie morgen Vormittag per E-Mail über den Status informiere.
<customer>: Gut. Wenn ich morgen nichts höre, rufe ich direkt Ihre Vorgesetzte an.
<agent>: Das verstehe ich. Ich kümmere mich darum, dass es gar nicht so weit kommt.
<customer>: Na gut, dann warte ich bis morgen.
<agent>: Vielen Dank, Frau Steiner. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for settlement of a claim. The agent finds an unposted invoice and prioritizes the case, including a personal status update the next day."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller speaking. I have a question about my premiums and payments.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What exactly is it about?
<customer>: I received a reminder yesterday, even though I'm sure I paid.
<agent>: Let's clarify this. Do you have the policy number at hand?
<customer>: Yes, PZ-2519-D4.
<agent>: Thanks. One moment... I see that the premium for the second quarter is still outstanding. Do you perhaps have a payment receipt or the date of the transfer?
<customer>: I paid in the middle of the month. Honestly, this is getting annoying, it's not the first time this happens.
<agent>: I understand that. If you want, you can send me the payment receipt by email, then we'll reconcile the payment with our bookings.
<customer>: Do I have to do this again? Can't you just check the bank?
<agent>: For data protection reasons, we only see our account movements. Without a receipt, it's difficult to search for a specific transfer. However, I can commission an internal reconciliation in parallel.
<customer>: Good, I'll forward you the screenshot from e-banking to keller@gmail.com. Are you using this address?
<agent>: Yes, exactly this one is registered. I'll note that the reminder fee is suspended for now until we've clarified the case.
<customer>: At least that. I definitely don't want to appear as a defaulting payer.
<agent>: That's understandable. As soon as we've found the payment receipt, you'll receive a confirmation and the reminder will be deleted.
<customer>: Okay, then I'll do that right after the phone call.
<agent>: Thank you very much, Mr. Keller. We'll take care of it.""",
        "topics": ["6"],
        "summary": "Customer receives a reminder despite having made payment. The agent suspends the reminder fee and requests payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Alonso. Ich habe einige Fragen zu den Leistungen meiner Gesundheitsunterstützung bei der Vaudoise.
<agent>: Guten Tag Frau Alonso, hier ist Anna Meier. Erzählen Sie mir, worum es konkret geht.
<customer>: Mein Arzt hat mir eine Psychotherapie empfohlen. Ich weiss aber nicht, was genau und wie lange die Vaudoise beteiligt ist.
<agent>: Dafür schauen wir am besten in Ihre Police. Haben Sie Ihre Policennummer zur Hand?
<customer>: Ja, GS-6059-J5.
<agent>: Danke, ich habe Ihre Unterlagen vor mir. Sie haben ein Zusatzpaket mit Beteiligung an ambulanten Therapien.
<customer>: Bedeutet das, dass alles übernommen wird?
<agent>: Nicht ganz. Ich erkläre es Ihnen Schritt für Schritt:
<agent>: Erstens: Es gibt einen Selbstbehalt von 10% auf die Kosten, nachdem die Franchise der Grundversicherung erreicht ist.
<customer>: Okay, und zweitens?
<agent>: Zweitens: Es ist eine maximale Anzahl von 40 Sitzungen pro Jahr vorgesehen, sofern die Therapie ärztlich verordnet und von einer anerkannten Fachperson durchgeführt wird.
<customer>: Und wenn ich mehr als 40 Sitzungen brauche?
<agent>: Drittens: Darüber hinaus gehende Sitzungen können auf Antrag geprüft werden, es gibt aber keine Garantie, dass sie übernommen werden.
<customer>: Verstehe. Viertens?
<agent>: Viertens: Für die erste Kostengutsprache benötigen wir einen Bericht Ihrer behandelnden Ärztin oder Ihres Arztes.
<customer>: Das heisst, ich muss zuerst zum Hausarzt?
<agent>: Genau, fünftens: Der Antrag muss über Ihre Hausärztin oder Ihren Hausarzt laufen. Sie oder er reicht die Unterlagen direkt bei uns ein.
<customer>: Puh, das ist komplizierter als gedacht, aber jetzt habe ich es verstanden.
<agent>: Gerne fasse ich Ihnen alles in einer E-Mail zusammen, damit Sie es in Ruhe nachlesen können. Ist alonso@hotmail.com noch aktuell?
<customer>: Ja, das passt.
<agent>: Wunderbar, dann sende ich Ihnen die Zusammenfassung und ein Merkblatt noch heute.
<customer>: Danke, das hilft mir sehr.
<agent>: Dafür sind wir da, Frau Alonso.""",
        "topics": ["7"],
        "summary": "Customer inquires about coverage for psychotherapy. The agent explains deductible, session count, and application process and sends a written summary."
    },
    {
        "transcript": """<customer>: Hallo, hier ist Herr Keller. Mein Auto ist eben liegengeblieben und ich brauche dringend Pannenhilfe.
<agent>: Guten Tag Herr Keller, hier ist Luca Steiner von der Vaudoise Assistance. Sind Sie und alle Mitfahrenden in Sicherheit?
<customer>: Ja, wir stehen auf einem Parkplatz, aber das Auto springt nicht mehr an.
<agent>: Gut, dann beruhigt mich das schon einmal. Wo genau befinden Sie sich?
<customer>: Auf der A2 Raststätte Richtung Luzern, kurz nach der Ausfahrt Sursee.
<agent>: Danke. Haben Sie Ihre Policennummer oder Ihr Kennzeichen zur Hand?
<customer>: Kennzeichen ist LU 123 456, Policennummer müsste PH-2385-L9 sein.
<agent>: Perfekt, ich sehe, Sie haben das erweiterte Pannenhilfe-Paket. Ich kann sofort einen Abschleppdienst organisieren.
<customer>: Wie lange dauert das ungefähr?
<agent>: Erfahrungsgemäss 30 bis 45 Minuten, je nach Verkehrslage. Der Pannendienst bringt Ihr Fahrzeug zu einer Partnergarage oder auf Wunsch zu Ihrer Stammgarage.
<customer>: In Ordnung. Und was kostet mich das?
<agent>: Der Einsatz selbst ist durch Ihre Pannenhilfe gedeckt. Allfällige Reparaturkosten in der Garage gehen separat.
<customer>: Gut, dann schicken Sie jemanden. Meine Handynummer ist dieselbe wie im System.
<agent>: Ich habe sie hier, der Pannendienst wird Sie kurz vor Ankunft direkt anrufen.
<customer>: Alles klar, danke.
<agent>: Gern geschehen, Herr Keller. Bleiben Sie unbedingt hinter der Leitplanke, falls Sie doch nahe der Autobahn stehen.""",
        "topics": ["8"],
        "summary": "Customer needs immediate roadside assistance on the highway. Assistance organizes a towing service that is covered by the roadside assistance package."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have a question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Marc Ducret from Vaudoise. What's the matter?
<customer>: We bought some new, quite expensive furniture. I'm not sure if the insurance sum is still sufficient.
<agent>: Then let's check that together. Do you have your policy number at hand?
<customer>: Yes, HR-8435-W3.
<agent>: Thanks. Your current insurance sum is 60,000 francs. Do you have an approximate idea of the total value of your household contents after the new purchase?
<customer>: Hard to say, but I think it's rather around 80,000 francs.
<agent>: Then there is indeed a risk of underinsurance. In case of damage, this would mean that compensations could be reduced.
<customer>: I definitely don't want that. But I also don't want to pay unnecessarily high premiums.
<agent>: Understandable. We could offer a free household contents check where you record a list of your largest items online. This results in a realistic insurance sum.
<customer>: Does someone have to come by?
<agent>: No, you can do that conveniently yourself. If you want, I can send you the link to the tool by email and then adjust the policy accordingly.
<customer>: Alright, let's do it that way.
<agent>: Perfect. I'll send you the link to steiner@gmail.com and a proposal for the new insurance sum.
<customer>: Good, then I'll look at that tonight.
<agent>: Thank you very much, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer has significantly upgraded her household contents and fears underinsurance. She receives an online tool to determine an appropriate insurance sum."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich habe Fragen zu meiner Fahrzeugversicherung bei der Vaudoise.
<agent>: Guten Tag Herr Simic, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich hatte einen Steinschlag in der Frontscheibe, und die Werkstatt meint, ich soll das über die Versicherung laufen lassen. Verliere ich dann meinen Bonus?
<agent>: Schauen wir zuerst in Ihre Police. Haben Sie die Nummer zur Hand?
<customer>: Ja, FV-1234-P3.
<agent>: Danke. Sie haben eine Vollkaskoversicherung mit einem speziellen Bonus-Schutz-Modul.
<customer>: Und was heisst das konkret?
<agent>: Das bedeutet, dass ein einzelner Glasschaden Ihren Bonus nicht reduziert. Sie zahlen nur die vereinbarte Selbstbeteiligung, falls überhaupt eine vorgesehen ist.
<customer>: Das klingt schon mal besser. Wie hoch ist die Selbstbeteiligung?
<agent>: Bei Glasschäden ist bei Ihnen keine Selbstbeteiligung hinterlegt.
<customer>: Also zahle ich gar nichts?
<agent>: Die Reparatur der Scheibe wäre in Ihrem Fall vollständig gedeckt, sofern sie bei einer anerkannten Partnerwerkstatt erfolgt.
<customer>: Okay, das ist fair. Können Sie mir eine Liste der Partnerwerkstätten in meiner Nähe per E-Mail senden?
<agent>: Sehr gerne. Ich sende Ihnen eine Übersicht für den Raum Luzern an simic@gmail.com.
<customer>: Super, dann bin ich zufrieden.
<agent>: Freut mich, dass ich helfen konnte, Herr Simic.""",
        "topics": ["10"],
        "summary": "Customer inquires whether glass damage affects his bonus. Thanks to bonus protection and no deductible, the repair is fully covered."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. J'ai une question sur mon assurance voyage.
<agent>: Bonjour Monsieur Berger, ici Marc Ducret de Vaudoise. De quoi s'agit-il?
<customer>: Je pars la semaine prochaine en Thaïlande. Comment cela se passe-t-il si je ne peux pas voyager à cause d'une maladie soudaine?
<agent>: Pour cela, je regarde rapidement dans votre police RV-1208-B3. Vous avez souscrit une assurance frais d'annulation.
<customer>: Et qu'est-ce que cela couvre exactement?
<agent>: Si vous ou une personne co-assurée tombez gravement malades ou avez un accident avant le voyage, nous prenons en charge les frais d'annulation contractuellement dus selon les conditions.
<customer>: Avez-vous alors besoin d'un certificat médical?
<agent>: Oui, une attestation médicale est requise, dont il ressort que le voyage ne peut pas être entrepris d'un point de vue médical.
<customer>: Et si un avertissement de voyage officiel est prononcé?
<agent>: Selon la situation, la couverture est examinée par le biais d'une autre clause, par exemple en cas de force majeure. Nous nous orientons également selon les conseils de voyage de la Confédération.
<customer>: Bien, au moins je ne suis pas complètement livré à moi-même.
<agent>: Exactement, vous avez une protection solide. Si vous voulez, je vous envoie un court mémo sur les points les plus importants.
<customer>: Oui, s'il vous plaît à berger@gmail.com.
<agent>: Je le fais volontiers, Monsieur Berger.""",
        "topics": ["11"],
        "summary": "Customer inquires about cancellation protection in case of illness and travel warnings. The agent explains coverage and requirements, including medical certificate."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Alonso. I have questions about my life insurance with Vaudoise.
<agent>: Good afternoon Mrs. Alonso, this is Sarah Dürst. What would you like to know?
<customer>: My life situation has changed, I now have a child. I'm wondering if the insurance sum is still sensible.
<agent>: Then it's a good time to look at that. Do you have your policy number ready?
<customer>: Yes, LV-4995-Q2.
<agent>: Thanks. Your current insurance sum is 100,000 francs. Do you have an idea of what you'd like as a target sum?
<customer>: Rather 200,000 francs, so that in the worst case at least the mortgage is partially covered.
<agent>: I understand. An increase is basically possible, but a renewed health examination may be required.
<customer>: What exactly does that mean?
<agent>: You would fill out a health questionnaire, and depending on the sum and age, a medical examination could be added.
<customer>: And if something is found?
<agent>: Then there can be reservations or a surcharge. I recommend that we first create a non-binding quote with different variants.
<customer>: Alright. Please send me two variants: one with 150,000 and one with 200,000.
<agent>: Very gladly. I'll send you the quotes to alonso@gmail.com.
<customer>: Thanks, then I'll discuss this with my partner.
<agent>: That's a good idea, Mrs. Alonso.""",
        "topics": ["12"],
        "summary": "Customer has had offspring and wants to increase the insurance sum of her life insurance. A quote with two variants and reference to possible health examination is created."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Wertsachenversicherung.
<agent>: Guten Tag Herr Keller, hier ist Anna Meier von der Vaudoise. Was liegt an?
<customer>: Ich habe eine neue Uhr gekauft, die nicht ganz billig war. Ich möchte wissen, ob die automatisch mitversichert ist.
<agent>: Haben Sie die Policennummer Ihrer Wertsachenversicherung?
<customer>: Ja, WV-6297-D2.
<agent>: Danke. Sie haben eine Pauschaldeckung für Wertsachen bis 20'000 Franken. Wissen Sie ungefähr, wo Sie aktuell mit dem Gesamtwert liegen?
<customer>: Mit der neuen Uhr komme ich wahrscheinlich knapp über 20'000 Franken.
<agent>: Dann wäre es sinnvoll, die Uhr entweder einzeln zu deklarieren oder die Pauschalsumme zu erhöhen.
<customer>: Und was empfehlen Sie?
<agent>: Wenn es sich um ein besonders wertvolles Einzelstück handelt, ist eine Einzeldeklaration vorteilhaft – unter anderem im Schadenfall.
<customer>: In Ordnung. Ich lasse Ihnen die Rechnung und ein Foto zukommen.
<agent>: Perfekt. Senden Sie die Unterlagen bitte an unsere E-Mail-Adresse, die ich Ihnen gleich per Mail zur Bestätigung schicke.
<customer>: Passt, danke.
<agent>: Sehr gerne, Herr Keller.""",
        "topics": ["13"],
        "summary": "Customer wants to insure a new, expensive watch. The agent recommends individual declaration or increasing the lump sum and requests documents."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about my insurance.
<agent>: Good afternoon Mr. Baumann, this is Pascal Tremblay from Vaudoise. What concerns you?
<customer>: I feel like I have too many individual policies and everything is too complicated.
<agent>: I hear that often. We can check a so-called policy bundling.
<customer>: What does that bring me?
<agent>: First: You have fewer documents and a better overview. Second: Often there's a bundling discount. Third: Adjustments can be made more easily.
<customer>: Sounds logical. But I don't want to suddenly be worse insured.
<agent>: I understand that. We would compare your existing coverage point by point:
<agent>: 1. Which risks are covered today?
<agent>: 2. Which coverage could be merged?
<agent>: 3. Where are there duplicate insurances?
<customer>: Duplicate insurances? That would be wasted money.
<agent>: Exactly, and fourth we would check whether the insurance sums still fit your current life situation.
<customer>: And how does that work concretely?
<agent>: I'll send you an overview of your policies in advance by email to baumann@hotmail.com. After that we can arrange a consultation appointment, by phone or on-site.
<customer>: A phone appointment is enough for me first.
<agent>: Good, I'll send you two appointment suggestions for next week right away.
<customer>: Alright, then I'll decide on one of them.
<agent>: Perfect, Mr. Baumann.""",
        "topics": ["1"],
        "summary": "Customer feels overwhelmed by the number of his policies. A bundling with possible discount and structured review of coverage is proposed.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich habe das Gefühl, dass ich bei Ihnen nicht ausreichend versichert bin.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Was lässt Sie das vermuten?
<customer>: Eine Freundin hatte einen Brand im Keller, und ein Teil war nicht gedeckt. Jetzt frage ich mich, ob ich auch so eine Lücke habe.
<agent>: Dann prüfen wir das besser. Haben Sie Ihre Policennummer oder Kundennummer zur Hand?
<customer>: UD-3205-U3.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung eine relativ tiefe Versicherungssumme ausweist und keine speziellen Zusatzdeckungen für Fahrräder oder Schmuck besitzt.
<customer>: Super. Und das haben Sie mir nicht mal aktiv gesagt.
<agent>: Es tut mir leid, wenn das bisher nicht ausführlich besprochen wurde. Wir können jetzt gemeinsam schauen, was Ihnen wichtig ist.
<customer>: Wichtig ist mir, dass ich im Ernstfall nicht pleite bin.
<agent>: Verstehe. Wir könnten:
<agent>: – die Versicherungssumme erhöhen,
<agent>: – eine spezielle Wertsachendeckung hinzufügen,
<agent>: – und prüfen, ob gewisse Risiken wie Elementarschäden besser abgedeckt werden sollten.
<customer>: Klingt nach höheren Kosten.
<agent>: Es würde die Prämie leicht erhöhen, aber ich kann Ihnen zwei Varianten erstellen: eine Minimalanpassung und eine umfassendere Lösung.
<customer>: Schicken Sie mir beides. Aber ehrlich: Wenn ich das Gefühl habe, dass Sie einfach nur verkaufen wollen, wechsle ich die Versicherung.
<agent>: Ich verstehe Ihre Sorge. Ich werde alles transparent aufschlüsseln, damit Sie selbst entscheiden können.
<customer>: Gut, dann schaue ich mir das an.
<agent>: Vielen Dank, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer suspects gaps in her household contents and valuables coverage. Various adjustment variants with different premium levels are announced.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une demande de vente.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer de Vaudoise. De quoi s'agit-il?
<customer>: Je déménage dans un nouvel appartement, et mon propriétaire exige une assurance responsabilité civile privée et ménage. Mais j'ai actuellement seulement l'assurance auto et voyage.
<agent>: Alors regardons comment nous pouvons compléter cela. Voulez-vous souscrire les deux - ménage et responsabilité civile privée - ensemble?
<customer>: Oui, mais cela ne doit pas être trop cher.
<agent>: Si nous définissons cela comme un paquet, nous pouvons offrir un rabais de combinaison.
<customer>: Pouvez-vous me donner une valeur indicative maintenant?
<agent>: Basé sur votre profil - lieu de résidence, âge et contrats déjà existants - j'estime environ 280 à 320 francs par an pour les deux ensemble.
<customer>: Cela va. Mais j'ai besoin de cela assez urgemment, sinon il y aura des problèmes avec le propriétaire.
<agent>: Nous pourrions créer aujourd'hui une attestation de couverture provisoire. Les documents définitifs, vous les recevrez ensuite par courrier ou email.
<customer>: D'accord. Alors faisons cela.
<agent>: Parfait. Je vous envoie d'abord un bref résumé par email à keller@gmail.com. Dès que vous confirmez, je génère l'attestation de couverture pour votre propriétaire.
<customer>: Faites vite s'il vous plaît, je dois lui donner cela au plus tard demain.
<agent>: Je m'en occupe tout de suite après, Monsieur Keller.""",
        "topics": ["3"],
        "summary": "Customer urgently needs household contents and personal liability insurance for a new apartment. A package with combination discount and provisional coverage certificate is offered."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverhandlung an, und ehrlich gesagt bin ich ziemlich sauer.
<agent>: Guten Tag Frau Dvorak, hier ist Marc Ducret. Es tut mir leid, dass Sie verärgert sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruch bei mir zuhause, Referenz SV-3253-C3. Sie haben diverse Positionen einfach gestrichen.
<agent>: Ich öffne den Fall… Einen Moment bitte… Ja, ich sehe die Korrespondenz. Einige Gegenstände konnten nicht belegt werden.
<customer>: Natürlich habe ich keine Rechnung von einer fünf Jahre alten Tasche mehr. Deswegen war sie ja trotzdem da!
<agent>: Ich verstehe Ihre Sicht. Gemäss Bedingungen sind wir aber auf Nachweise angewiesen, damit wir den Wert einschätzen können.
<customer>: Also glauben Sie mir einfach nicht? Super.
<agent>: Darum geht es nicht. Wir brauchen Anhaltspunkte, zum Beispiel Fotos, Kontoauszüge oder Garantiekarten.
<customer>: Das habe ich schon alles geschickt. Lesen Sie Ihre Mails?
<agent>: Ich sehe, dass gestern tatsächlich noch Fotos nachgereicht wurden, die aber noch nicht im System verknüpft sind. Das hätte schneller gehen müssen, entschuldigen Sie bitte.
<customer>: Ich habe langsam das Gefühl, ich werde hingehalten, damit ich aufgebe.
<agent>: Das ist ganz sicher nicht die Absicht. Ich werde den Fall noch heute an die zuständige Fachperson weitergeben und um eine erneute Prüfung der abgelehnten Positionen bitten.
<customer>: Gut. Wenn sich nichts bewegt, gehe ich damit zur Presse. Das meine ich ernst.
<agent>: Ich nehme Ihre Beschwerde sehr ernst und vermerke sie entsprechend. Sie erhalten bis spätestens Anfang nächster Woche eine schriftliche Stellungnahme.
<customer>: Wir werden sehen.
<agent>: Danke, dass Sie uns trotzdem noch einmal die Chance geben, das zu klären.""",
        "topics": ["4"],
        "summary": "Customer is annoyed about the rejection of burglary claim positions. After submitted photos, a new review is promised and the complaint is noted in the file."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Keller. I'm calling again about my open claim.
<agent>: Good afternoon Mr. Keller, this is Sarah Dürst from Vaudoise. Which claim is it about?
<customer>: Claim No. SN-5073-J8. I was told I would receive a payout last week. So far nothing is there.
<agent>: Let me check... It seems that the payment was released internally, but the bank connection was incomplete.
<customer>: You've had that from me a thousand times already!
<agent>: I see that the IBAN in the system is registered with two digits too few. That's naturally annoying, I'm sorry.
<customer>: That's more than annoying. I'm waiting for the money.
<agent>: Please give me your complete IBAN again so we can correct this.
<customer>: CH12 3456 7890 1234 5678 9.
<agent>: Thanks. I'll correct this immediately and forward the payment for processing again. Additionally, I'll note that any default interest should be checked.
<customer>: At least something. But quite honestly, the trust is pretty much gone by now.
<agent>: I can understand that. I can offer to send you a written confirmation about the renewed triggering this afternoon.
<customer>: Yes, I expect that too.
<agent>: Alright, Mr. Keller. Again, sorry for the circumstances.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for claim payment. Due to incorrect IBAN the payout was delayed, which is now corrected and triggered again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe schon wieder ein Schreiben zu offenen Prämien bekommen.
<agent>: Guten Tag Frau Roth, hier ist Yann Morel von der Vaudoise. Dann schauen wir uns das an. Haben Sie eine Referenznummer?
<customer>: Auf dem Brief steht PZ-6667-O4.
<agent>: Danke. Ich sehe, dass es sich um eine Prämienerhöhung aufgrund einer Vertragsverlängerung handelt. Vielleicht wirkt das wie ein neuer offener Betrag.
<customer>: Aber es ist deutlich mehr als letztes Jahr. Das kann doch nicht sein.
<agent>: Die Prämie wurde aufgrund höherer Schadenbelastung in Ihrem Segment angepasst. Zusätzlich ist eine Indexierung eingeflossen.
<customer>: Das heisst auf gut Deutsch: Ich zahle mehr, ohne dass ich etwas dafür bekomme.
<agent>: Die Deckung bleibt zwar gleich, aber die Kosten im Hintergrund steigen. Auf Wunsch könnten wir Deckungen anpassen, um die Prämie zu reduzieren.
<customer>: Zum Beispiel?
<agent>: Man könnte die Selbstbeteiligung leicht erhöhen oder einzelne optionale Zusatzbausteine streichen.
<customer>: Und wenn ich das nicht will?
<agent>: Dann bleibt die Prämie wie im Schreiben angegeben. Selbstverständlich steht es Ihnen frei, den Markt zu vergleichen.
<customer>: Vielleicht mache ich das. Im Moment bin ich wirklich nicht begeistert.
<agent>: Das verstehe ich. Wenn Sie möchten, kann ich Ihnen mindestens ein oder zwei Sparvarianten ausrechnen und per E-Mail senden.
<customer>: Schicken Sie es an roth@gmail.com. Aber ohne Schönrederei.
<agent>: Ich sende Ihnen eine nüchterne Aufstellung, versprochen.""",
        "topics": ["6"],
        "summary": "Customer is annoyed about a significant premium increase. The agent explains reasons and offers savings variants through coverage adjustment."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. J'ai des questions de santé en relation avec ma police.
<agent>: Bonjour Madame Roth, ici Pascal Tremblay. En quoi puis-je vous aider?
<customer>: J'ai été inscrite pour une réhabilitation, et la clinique veut savoir ce que Vaudoise prend exactement en charge.
<agent>: Alors regardons dans votre police GS-1199-B4. Vous avez un paquet de réha avec une durée limitée.
<customer>: Combien de temps exactement?
<agent>: En principe, 21 jours de réha stationnaire par an sont couverts, pour autant qu'elle soit médicalement indiquée et approuvée au préalable.
<customer>: Mon médecin a dit que j'ai besoin d'au moins quatre semaines.
<agent>: Les jours supplémentaires pourraient passer par l'assurance de base ou un examen de cas individuel. Nous avons besoin pour cela d'un rapport détaillé de votre médecin.
<customer>: Et si cela est refusé?
<agent>: Alors les coûts supplémentaires seraient en partie ou entièrement à votre charge. Je recommande que nous demandions d'abord l'autorisation de coûts pour les 21 jours et examinions la prolongation en parallèle.
<customer>: D'accord, envoyez-moi une liste de ce que mon médecin doit soumettre.
<agent>: Très volontiers, je vous envoie un mémo à roth@gmail.com.
<customer>: Merci. J'espère que cela fonctionne sans paperasserie interminable.
<agent>: Nous essayons de garder le processus aussi simple que possible.""",
        "topics": ["7"],
        "summary": "Customer needs clarity about rehabilitation benefits. 21 days of rehabilitation are covered, an extension will be reviewed based on medical report."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich rufe wegen meiner Pannenhilfe an – beziehungsweise wegen deren Grenzen.
<agent>: Guten Tag Frau Roth, hier ist Nora Widmer von der Vaudoise. Was ist passiert?
<customer>: Gestern Nacht ist mein Auto in Deutschland stehen geblieben, und mir wurde gesagt, das sei nicht gedeckt.
<agent>: Ich schaue in Ihre Police PH-5104-L8… Sie haben eine Pannenhilfe, die standardmässig auf die Schweiz und das Fürstentum Liechtenstein beschränkt ist.
<customer>: Ja, das hat mir der Herr am Telefon dann auch gesagt – aber ganz ehrlich, das hätte man mir früher sagen müssen.
<agent>: Ich verstehe Ihren Ärger. Für Fahrten ins Ausland empfehlen wir ein erweitertes Assistance-Paket.
<customer>: Ja, jetzt weiss ich das auch. Bringt mir nur nichts mehr, das Taxi und der Rücktransport haben mich ein Vermögen gekostet.
<agent>: Für diesen konkreten Fall können wir leider nichts mehr rückwirkend decken. Was ich tun kann, ist Ihnen ein Angebot für die Zukunft zu machen.
<customer>: Das ist wenig tröstlich. Ich überlege mir ernsthaft, die Versicherung zu wechseln.
<agent>: Das tut mir sehr leid zu hören. Ich würde dennoch gerne sicherstellen, dass Sie künftig besser geschützt sind – ob bei uns oder anderswo. Darf ich Ihnen eine Übersicht über die möglichen Ausland-Assistance-Varianten schicken?
<customer>: Meinetwegen. Aber ehrlich, ich bin enttäuscht.
<agent>: Das kann ich nachvollziehen. Ich sende Ihnen die Übersicht an roth@gmail.com.
<customer>: Tun Sie das. Ich entscheide dann, ob ich bleibe.
<agent>: Danke, dass Sie uns trotzdem noch eine Chance geben, Frau Roth.""",
        "topics": ["8"],
        "summary": "Customer had a breakdown abroad that wasn't covered and is disappointed. The agent explains coverage limits and offers future foreign assistance options."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have another question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner from Vaudoise. What can I do for you?
<customer>: After the last phone call, I looked at your documents and found that my basement isn't specifically mentioned.
<agent>: Basement compartments are usually co-insured as long as they're at the same location. Let me quickly check your policy HR-1056-J5.
<customer>: But my basement is in the neighboring house. Does that count too?
<agent>: That's an important difference. If it's in another building, it might need a special agreement.
<customer>: And why doesn't anyone tell me this when I take out the policy?
<agent>: That could have been communicated more clearly, you're right there. But we can catch up on this now and explicitly include your basement in the policy.
<customer>: What does that cost me?
<agent>: That depends on the value of the stored items. If you give me a rough estimate, I can create a quote.
<customer>: Let's say 8,000 francs.
<agent>: Alright. I'll create a quote for you and send it to steiner@gmail.com. Only when you agree in writing will the coverage be extended.
<customer>: Good. This time I'll read everything very carefully.
<agent>: That's very sensible, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer discovers that her external basement compartment isn't clearly mentioned. A special agreement with quote for co-insurance is proposed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Es geht um meine Fahrzeugversicherung.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Worum geht es genau?
<customer>: Ich habe einen Brief bekommen, dass meine Kaskoversicherung wegen ausstehender Zahlung gesperrt wurde. Ich bin aber sicher, dass ich bezahlt habe.
<agent>: Lassen Sie mich Ihre Police FV-5163-G4 öffnen. Ich sehe hier tatsächlich eine temporäre Sistierung.
<customer>: Was heisst das konkret? Wenn ich jetzt einen Unfall habe, bin ich nicht versichert?
<agent>: Die Haftpflichtdeckung bleibt bestehen, aber Kaskoschäden wären momentan nicht gedeckt.
<customer>: Das ist ja wohl ein Witz. Ich habe vor zwei Wochen überwiesen.
<agent>: Es tut mir sehr leid. Wenn Sie möchten, können wir zusammen nachsehen, ob wir die Zahlung bereits erhalten haben und sie nur noch nicht zugeordnet wurde.
<customer>: Ich habe gerade keinen Beleg zur Hand, aber ich kann Ihnen später einen Screenshot schicken.
<agent>: Das wäre hilfreich. Alternativ könnten Sie den Betrag heute nochmals überweisen und wir würden bei Doppelzahlung umgehend zurückerstatten.
<customer>: Sicher nicht. Ich zahle nicht doppelt.
<agent>: Das verstehe ich. Dann warten wir auf Ihren Screenshot, setzen die Sistierung aber schon heute zur Überprüfung auf Priorität.
<customer>: Machen Sie das. Und bitte informieren Sie mich schriftlich, sobald alles wieder aktiv ist.
<agent>: Selbstverständlich, Frau Dvorak.""",
        "topics": ["10"],
        "summary": "Customer is annoyed about suspension of comprehensive coverage due to allegedly outstanding premium. She doesn't want to pay double amount and sends payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Baumann. I have a question about my travel insurance.
<agent>: Hello Mr. Baumann, this is Anna Meier from Vaudoise. What's it about?
<customer>: My flight was cancelled by the airline, and I was told I need to handle this through my insurance.
<agent>: Let me check your policy RV-7970-V7. Basically, in case of flight cancellations, the airline is primarily responsible.
<customer>: Yes, but they're currently pushing it to "force majeure" and only want to give me a voucher.
<agent>: In such cases, your travel insurance can partially help, for example with additional costs for hotel or replacement flight, depending on the cause.
<customer>: It was a strike. Does that count?
<agent>: Strikes are covered to a limited extent in many policies. I see that your contract provides certain benefits, but only under certain conditions.
<customer>: Quite honestly, I feel like I'm being pushed around between airline and insurance.
<agent>: I can understand that well. What I can do: Send us the written statement from the airline, and we'll check specifically which positions we can cover.
<customer>: Good, then I'll do that. But I expect a clear answer, not just paragraphs.
<agent>: I'll explicitly note this hint in the file so that the answer is formulated as understandably as possible.""",
        "topics": ["11"],
        "summary": "Customer is caught between airline and insurance after flight cancellation. The agent requests documents to check travel insurance coverage for strikes."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer von der Vaudoise. Wie kann ich helfen?
<customer>: Ich überlege mir, die Police ganz zu kündigen. Ich zahle schon so viel und habe das Gefühl, ich brauche das nicht.
<agent>: Dann sollten wir gemeinsam anschauen, was die Konsequenzen wären. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-5949-B6.
<agent>: Danke. Bei einer Kündigung jetzt würden Sie einen Rückkaufswert erhalten, der unter der bisher einbezahlten Summe liegt.
<customer>: Das klingt nicht gerade attraktiv.
<agent>: Nein, kurzfristig ist der Rückkaufswert oft tiefer. Langfristig bietet die Police einen Todesfallschutz und teilweise auch Sparkomponenten.
<customer>: Ich weiss, aber das Geld fehlt mir im Alltag.
<agent>: Eine Alternative wäre, die Prämie zu reduzieren oder den Vertrag für eine gewisse Zeit prämienfrei zu stellen, anstatt ihn ganz zu beenden.
<customer>: Heisst das, ich würde vorübergehend nichts mehr zahlen?
<agent>: Genau. Die Leistungen würden entsprechend reduziert, aber der Vertrag bliebe bestehen.
<customer>: Schicken Sie mir bitte beide Varianten: Kündigung mit Rückkaufswert und Prämienreduktion.
<agent>: Sehr gerne, ich sende Ihnen eine Übersicht an baumann@hotmail.com.
<customer>: Dann entscheide ich danach.
<agent>: Das klingt gut, Herr Baumann.""",
        "topics": ["12"],
        "summary": "Customer thinks about cancelling life insurance. Alternatives like premium reduction or premium-free continuation are shown."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer. Que voulez-vous savoir?
<customer>: J'ai acheté des bijoux à l'étranger. Sont-ils déjà assurés sur le chemin du retour ou seulement quand ils sont à la maison?
<agent>: Un bon point. Dans votre police WV-3507-W9, les objets de valeur sont assurés mondialement contre le vol, pour autant que certaines prescriptions de sécurité soient respectées.
<customer>: Quelles prescriptions?
<agent>: Par exemple, vous ne devez pas laisser les bijoux sans surveillance dans la voiture, et à l'hôtel vous devez utiliser le coffre-fort, s'il y en a un.
<customer>: Et si quelqu'un m'arrache le sac dans la rue?
<agent>: S'il s'agit d'un vol, ce serait en règle générale couvert, tant que vous n'avez pas agi avec négligence grave.
<customer>: D'accord, cela me rassure un peu. Alors j'espère que rien n'arrive du tout.
<agent>: Nous l'espérons aussi. Si vous voulez, vous pouvez nous envoyer après le retour une copie des justificatifs d'achat, pour que les valeurs soient actualisées dans le système.
<customer>: Je le fais.
<agent>: Parfait, Monsieur Keller.""",
        "topics": ["13"],
        "summary": "Customer asks about worldwide coverage of his newly acquired jewelry. The agent explains conditions and recommends submitting purchase receipts for updating."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. Another general question about Vaudoise.
<agent>: Good afternoon Mrs. Steiner, this is Pascal Tremblay. What's it about?
<customer>: I'm considering bundling all my insurance with a single provider. Before I do this with you, I want to know if I really only have one contact person in case of damage.
<agent>: A justified question. With us you receive a main contact who coordinates your files, even when various specialist departments are involved.
<customer>: Does that mean I don't have to tell everything multiple times?
<agent>: Exactly. Your main contact has access to relevant information and can internally involve the right places.
<customer>: Good, because this constant repetition annoys me with other providers.
<agent>: If you want, we can arrange a personal appointment where we go through your existing insurance and make a bundling offer.
<customer>: Send me a rough overview first before I invest time in an appointment.
<agent>: Of course, I'll send you an initial rough concept to steiner@gmail.com.
<customer>: Good, then we'll see further.
<agent>: Very gladly, Mrs. Steiner.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance with Vaudoise and asks about a central contact person. A rough concept is promised by email."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Simic. Je crains de ne pas avoir assuré certaines choses qui me sont importantes.
<agent>: Bonjour Monsieur Simic, ici Pascal Tremblay de Vaudoise. Quelles choses voulez-vous dire concrètement?
<customer>: Je travaille parfois depuis la maison et j'ai un équipement informatique coûteux dans le home office. Cela n'est mentionné nulle part explicitement.
<agent>: Je regarde dans vos documents avec la référence UD-2064-E3. Votre assurance ménage couvre en principe aussi les appareils de travail, mais seulement jusqu'à un certain montant.
<customer>: Et si la valeur est au-dessus?
<agent>: Alors nous aurions effectivement une lacune. Dans de nombreux cas, cela peut être comblé avec un module supplémentaire ou une solution d'affaires spéciale.
<customer>: Je ne veux pas soudainement entendre que c'est ma faute si on cambriole.
<agent>: C'est compréhensible. Je propose que nous saisissions la valeur approximative de votre équipement et que je calcule une couverture supplémentaire appropriée.
<customer>: Faites cela. Si c'est complètement excessif, je me cherche une autre solution.
<agent>: J'essaie de créer une offre équitable et transparente. Vous la recevrez à simic@gmail.com.
<customer>: D'accord.
<agent>: Merci, Monsieur Simic.""",
        "topics": ["2"],
        "summary": "Customer is unsure whether his home office equipment is sufficiently insured. The agent checks household contents coverage and creates an additional quote."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich wurde von einem Kollegen auf eine Kombi-Lösung bei der Vaudoise aufmerksam gemacht.
<agent>: Guten Tag Herr Simic, hier ist Marc Ducret. Meint Ihr Kollege vielleicht ein Paket aus Auto-, Hausrat- und Privathaftpflichtversicherung?
<customer>: Genau. Ich habe bisher nur die Fahrzeugversicherung bei Ihnen.
<agent>: Dann könnte sich ein Wechsel der anderen Versicherungen zu uns tatsächlich lohnen. Wir bieten bei Paketlösungen Rabatte an.
<customer>: Aber ich will keine Hochglanzverkaufsshow, nur klare Zahlen.
<agent>: Verstehe ich gut. Ich kann Ihnen auf Basis Ihrer aktuellen Situation eine nüchterne Vergleichsrechnung machen.
<customer>: Gut. Wenn sich nichts wirklich ändert, bleibe ich, wie ich bin.
<agent>: Das ist fair. Ich sende Ihnen eine Gegenüberstellung „Heute vs. Paketlösung" an simic@gmail.com.
<customer>: In Ordnung.
<agent>: Vielen Dank, dass Sie eine Paketlösung überhaupt in Betracht ziehen, Herr Simic.""",
        "topics": ["3"],
        "summary": "Customer is interested in a package solution with discounts but wants a clear numerical basis. A comparison calculation is created.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I'm calling again about my claim negotiation - I'm getting fed up.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner. I remember your case SV-6926-G8. What's currently the problem?
<customer>: I was promised on the phone that the deductible would be reduced, and now the original amount is in the letter again.
<agent>: Let me look at the notes... Indeed, it says here that a reduction was put in prospect, but apparently wasn't definitively approved yet.
<customer>: For me it came across like a commitment. I feel fooled.
<agent>: That was unfortunately formulated, I admit. I can now discuss the case directly with claims management.
<customer>: I expect you to keep your word - even if it was only "put in prospect".
<agent>: I understand your position. Can we do it like this: I'll get back to you by tomorrow with a final decision. Should the reduction be rejected, you'll receive a written justification.
<customer>: And if they write unclearly again, like before?
<agent>: I'll ask that the formulation be particularly understandable. And if you want, I'll additionally call you to explain everything personally.
<customer>: Alright. But this is your last chance, otherwise I'm gone.
<agent>: I take that very seriously, Mrs. Steiner.""",
        "topics": ["4"],
        "summary": "Customer is annoyed because a promised deductible reduction wasn't implemented in the letter. The case is clarified directly with claims management."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Schaden-Nachverfolgung.
<agent>: Guten Tag Herr Keller, hier ist Sarah Dürst. Um welchen Schaden geht es?
<customer>: SN-5675-E1, der Sturmschaden an meinem Dach. Ich weiss nicht, ob der Kostenvoranschlag akzeptiert wurde.
<agent>: Ich schaue… Ja, der Kostenvoranschlag der Firma wurde heute Morgen genehmigt.
<customer>: Aha, davon weiss ich nichts.
<agent>: Es hätte eine automatische E-Mail ausgelöst werden sollen. Offenbar hat das noch nicht geklappt.
<customer>: Das wundert mich nicht. Ich habe ohnehin das Gefühl, immer hinterherlaufen zu müssen.
<agent>: Es tut mir leid, dass dieser Eindruck entsteht. Ich sende Ihnen die Bestätigung gleich manuell zu.
<customer>: Gut. Und wann sehe ich das Geld?
<agent>: Die Auszahlung erfolgt nach Einreichen der Schlussrechnung. Bis dahin können Sie mit der Reparatur starten.
<customer>: Na gut, dann mache ich das so.
<agent>: Danke für Ihr Verständnis, Herr Keller.""",
        "topics": ["5"],
        "summary": "Customer waits for feedback on storm damage. The cost estimate is already approved, but the automatic notification didn't work; it's now sent manually."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller. I have a question about a premium invoice.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What's wrong with the invoice?
<customer>: Suddenly an annual payment is debited instead of a semi-annual one. I didn't change anything.
<agent>: Let me check your policy PZ-2949-B2. Here I see a changeover per contract renewal, where it was switched to annual payment by default.
<customer>: Without me signing anything?
<agent>: There was information in the renewal letter. If you don't agree with this, we can go back to semi-annual payment method.
<customer>: Yes, please. I can't just pay the whole amount at once.
<agent>: No problem. I'll reset the payment method, and the currently due invoice will be adjusted accordingly.
<customer>: Good. And please highlight such things more clearly next time.
<agent>: I'll gladly pass on your feedback, Mr. Keller.""",
        "topics": ["6"],
        "summary": "Customer notices a switch from semi-annual to annual payment method without his active involvement. The payment method is adjusted again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Berger. Ich wollte mich nach einer Unterstützung im Bereich Gesundheit erkundigen.
<agent>: Guten Tag Herr Berger, hier ist Yann Morel. Was genau interessiert Sie?
<customer>: Ich würde gerne an einem Präventionskurs für Rückentraining teilnehmen. Wird das teilweise übernommen?
<agent>: In Ihrer Police GS-8082-V9 gibt es ein Präventionsbudget, das für anerkannte Kurse genutzt werden kann.
<customer>: Wie hoch ist dieses Budget?
<agent>: Pro Jahr stehen Ihnen 300 Franken zur Verfügung, wenn der Kurs gewisse Kriterien erfüllt.
<customer>: Was für Kriterien?
<agent>: Der Anbieter muss zertifiziert sein, und der Kurs muss ein definiertes Programm umfassen, zum Beispiel über acht bis zehn Wochen.
<customer>: Okay, dann frage ich beim Kursanbieter nach einer Bestätigung.
<agent>: Genau, und schicken Sie uns danach die Kursbestätigung und Zahlungsbelege.
<customer>: Gut, dann mache ich das so.
<agent>: Perfekt, Herr Berger. So können Sie etwas für Ihren Rücken tun und gleichzeitig von der Versicherung profitieren.""",
        "topics": ["7"],
        "summary": "Customer inquires about prevention services for a back course. There is an annual prevention budget if course and provider meet certain criteria."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. Je voulais encore savoir quelque chose sur l'assistance panne.
<agent>: Bonjour Monsieur Berger, ici Yann Morel. Volontiers, que voulez-vous savoir?
<customer>: L'assistance panne vaut-elle aussi pour la voiture de ma partenaire si je conduis?
<agent>: Je regarde dans votre police PH-1780-E5. Dans votre cas, l'assistance panne est liée au véhicule, pas à la personne.
<customer>: Cela signifie que si je conduis avec sa voiture, je n'ai pas de chance?
<agent>: Pour cette voiture, votre assistance panne ne serait effectivement pas valable. Il faudrait une couverture propre ou une solution basée sur la personne.
<customer>: Eh bien, bravo. C'est sûrement écrit tout petit quelque part dans le texte, ou?
<agent>: C'est dans les conditions, oui, mais je comprends qu'on puisse facilement passer à côté.
<customer>: Franchement, cela m'énerve passablement.
<agent>: Je peux le comprendre. Si votre partenaire veut, nous pouvons examiner si une option assistance panne pour son véhicule ou une assistance basée sur les personnes en vaut la peine.
<customer>: Envoyez-moi d'abord des infos avant que je signe encore quelque chose.
<agent>: Très volontiers, je vous envoie un aperçu avec les deux possibilités à berger@gmail.com.""",
        "topics": ["8"],
        "summary": "Customer learns that his roadside assistance is vehicle-related and doesn't apply to his partner's car. He receives information about possible additional solutions."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I'm calling about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. How can I help?
<customer>: I've gone through your long policy and am honestly completely overwhelmed by the technical terms.
<agent>: Many people feel that way. Are there specific points that are unclear to you?
<customer>: For example, what exactly "new value compensation" means.
<agent>: That means that in case of damage we basically replace the replacement value of an equivalent new item, not just the time value.
<customer>: That at least sounds good. And what about things that are no longer manufactured?
<agent>: Then a comparable product or the monetary value is replaced.
<customer>: Could you perhaps send me a simplified summary of the most important points?
<agent>: Very gladly, I can create a simplified coverage sheet for you and send it to dvorak@hotmail.com.
<customer>: That would be great, then I finally understand what I actually bought.
<agent>: Very gladly, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is overwhelmed by technical terms in the property policy. The agent explains new value compensation and sends a simplified summary."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Worum geht es?
<customer>: Ich möchte wissen, ob sich ein Wechsel von Vollkasko auf Teilkasko lohnt. Mein Auto ist schon älter.
<agent>: Wie alt ist das Fahrzeug?
<customer>: Acht Jahre.
<agent>: Oft lohnt sich ab einem gewissen Fahrzeugalter tatsächlich ein Wechsel. Ich sehe in Ihrer Police FV-6623-H3, dass der Zeitwert schon deutlich gesunken ist.
<customer>: Und was spare ich ungefähr?
<agent>: Grob geschätzt könnten Sie rund 25 bis 30 Prozent der Prämie sparen.
<customer>: Und was verliere ich dafür?
<agent>: Sie wären bei selbstverschuldeten Kollisionen nicht mehr gedeckt, nur noch bei Ereignissen wie Diebstahl, Brand, Glasbruch, Elementarschäden und so weiter.
<customer>: Hm, ich denke, das Risiko kann ich eingehen.
<agent>: Wenn Sie möchten, kann ich eine Offerte für die Umstellung erstellen. Sie müssen diese dann nur noch bestätigen.
<customer>: Ja, schicken Sie sie mir.
<agent>: Gerne an keller@gmail.com.
<customer>: Genau.
<agent>: Dann mache ich das gleich, Herr Keller.""",
        "topics": ["10"],
        "summary": "Customer checks switching from comprehensive to partial coverage for an older vehicle. He receives a quote with premium savings and changed coverage."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe Fragen zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Was möchten Sie wissen?
<customer>: Ich plane eine Weltreise über mehrere Monate. Deckt meine aktuelle Police das überhaupt ab?
<agent>: Ich sehe mir Ihre Police RV-8954-C5 an. Sie ist primär für einzelne Reisen bis maximal 90 Tage ausgelegt.
<customer>: Meine Reise dauert aber mindestens sechs Monate.
<agent>: Dann reicht die aktuelle Police nicht aus. Wir müssten eine spezielle Langzeit-Reiselösung prüfen.
<customer>: Und warum steht das nicht klar irgendwo drauf?
<agent>: Es steht in den Bedingungen, aber ich gebe Ihnen recht, für längere Reisen ist das nicht sofort ersichtlich.
<customer>: Ganz ehrlich, das hätte ich fast übersehen. Ich wäre monatelang unterwegs gewesen und hätte gedacht, ich sei versichert.
<agent>: Gut, dass Sie vorher nachfragen. Ich kann Ihnen eine Offerte für eine Langzeitlösung erstellen oder, falls gewünscht, andere Optionen mit Ihnen besprechen.
<customer>: Schicken Sie mir eine Offerte, alles weitere sehe ich dann.
<agent>: Gerne, an roth@gmail.com.
<customer>: Ja, genau.
<agent>: Vielen Dank, Frau Roth.""",
        "topics": ["11"],
        "summary": "Customer plans a multi-month world trip. Her standard travel insurance only covers trips up to 90 days, so a long-term solution is created as a quote."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about Vaudoise.
<agent>: Good afternoon Mr. Baumann, this is Yann Morel. How can I help you?
<customer>: I'm wondering if I still need my existing insurance at all or if I'm over-insured.
<agent>: A justified question. We can do a so-called needs analysis.
<customer>: And does that mean you then want to sell me even more?
<agent>: Not necessarily. The goal is to find out what really fits your situation - that can also mean reducing something.
<customer>: That would be important to me.
<agent>: If you want, I'll send you a short questionnaire about household, income, family and assets. On this basis we can then review your coverage.
<customer>: Send it to baumann@gmail.com, but without marketing phrases.
<agent>: Understood, Mr. Baumann. I'll stick to the facts.""",
        "topics": ["1"],
        "summary": "Customer fears over-insurance. The agent offers a needs analysis via questionnaire where reductions are also possible.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Roth. I have another question about unmet insurance needs.
<agent>: Good afternoon Mrs. Roth, this is Sarah Dürst. What specifically is it about?
<customer>: I have a dog and I'm wondering if I need special liability insurance for that.
<agent>: In your personal liability insurance, pets are partially co-covered, depending on type and use. Let me quickly check this based on your file UD-4270-U4.
<customer>: He's a normal family dog, not a listed breed or anything.
<agent>: Then he would basically be co-insured, although there are maximum amounts and exclusions.
<customer>: And if he bites someone?
<agent>: Such damage would normally be covered, provided you meet the duty of care.
<customer>: Okay, that reassures me. So I don't need an extra policy?
<agent>: Not necessarily in your case. However, there are special animal owner policies with extended benefits if you want that.
<customer>: No, if it's sufficient like this, let's leave it at that.
<agent>: Alright, then there's no additional need in this area.""",
        "topics": ["2"],
        "summary": "Customer asks if her dog is sufficiently covered by personal liability insurance. There is basic coverage, so no additional policy is necessarily needed."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Steiner. J'ai une demande de vente.
<agent>: Bonjour Madame Steiner, ici Yann Morel. Qu'est-ce qui vous intéresse?
<customer>: J'ai pensé à souscrire une petite assurance vie pour la sécurité de mes enfants.
<agent>: C'est un sujet sensé. Avez-vous déjà une idée de la somme d'assurance souhaitée?
<customer>: Peut-être 50'000 francs par enfant.
<agent>: Nous pourrions établir une police avec une durée fixe jusqu'à un certain âge de vos enfants.
<customer>: Et qu'est-ce que cela me coûterait approximativement?
<agent>: Cela dépend de votre âge et de votre état de santé. En gros, nous sommes à quelques centaines de francs par an.
<customer>: Envoyez-moi s'il vous plaît une offre concrète. Je ne veux décider qu'une fois que j'ai vu les chiffres.
<agent>: Très volontiers, je vous envoie une offre avec deux variantes à steiner@gmail.com.
<customer>: Bien, alors je réfléchis à cela.
<agent>: Parfait, Madame Steiner.""",
        "topics": ["3"],
        "summary": "Customer is interested in a small life insurance for securing her children. She receives a quote with various variants."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverfolgung an – schon wieder.
<agent>: Guten Tag Frau Dvorak, hier ist Anna Meier. Es tut mir leid, dass Sie erneut anrufen müssen. Um welchen Schaden geht es?
<customer>: Um den Wasserschaden von letzter Woche, SN-4974-L3. Mir wurde ein Rückruf versprochen, aber niemand hat sich gemeldet.
<agent>: Ich sehe im System tatsächlich einen offenen Rückrufauftrag, der noch nicht erledigt wurde. Das hätte nicht passieren dürfen.
<customer>: So langsam glaube ich Ihnen gar nichts mehr.
<agent>: Ich verstehe Ihren Frust und entschuldige mich dafür. Ich kann Ihnen jetzt direkt Auskunft geben, wenn Sie möchten.
<customer>: Ja, bitte.
<agent>: Die Offerte des Handwerkers wurde genehmigt, Sie können mit der Reparatur beginnen. Die Zahlung erfolgt nach Eingang der Schlussrechnung.
<customer>: Warum sagt mir das niemand einfach rechtzeitig?
<agent>: Wir müssen unsere internen Abläufe verbessern, das ist offensichtlich. Ich werde den Vorgang als Beschwerde markieren.
<customer>: Tun Sie das. Vielleicht ändert sich dann etwas.
<agent>: Ich hoffe es auch, Frau Dvorak.""",
        "topics": ["5"],
        "summary": "Customer is annoyed because promised callbacks were missed. The approved claim is explained and the process is noted as a complaint."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Alonso. J'ai une question sur mes primes.
<agent>: Bonjour Madame Alonso, ici Marc Ducret. Que voulez-vous savoir?
<customer>: J'ai vu que j'ai un rabais pour plusieurs produits. Si j'annule une police, est-ce que je perds le rabais sur toutes les autres?
<agent>: Je vérifie votre police PZ-1231-V4. Votre rabais multiple dépend de trois produits de base: ménage, responsabilité civile et assurance véhicule.
<customer>: Et si je change l'assurance véhicule chez un autre fournisseur?
<agent>: Alors le rabais multiple serait réduit ou supprimé, ce qui peut conduire à des primes plus élevées sur les polices restantes.
<customer>: Donc à la fin, je ne fais peut-être aucun gain si je ne change qu'un contrat?
<agent>: Exactement, c'est pourquoi il vaut la peine de considérer l'effet global.
<customer>: Envoyez-moi s'il vous plaît une comparaison "avec assurance véhicule chez vous" et "sans".
<agent>: Très volontiers, je vous envoie cette comparaison à alonso@gmail.com.
<customer>: Alors je calcule tranquillement.
<agent>: C'est une très bonne idée, Madame Alonso.""",
        "topics": ["6"],
        "summary": "Customer wants to know how cancelling vehicle insurance affects her multiple discount. She receives a comparison of total premiums."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich habe eine Frage zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer. Worum geht es?
<customer>: Mein Zahnarzt hat mir eine Zahnreinigung empfohlen, die ziemlich teuer ist. Zahlt die Vaudoise etwas daran?
<agent>: In Ihrer Police GS-9392-W8 ist eine Beteiligung an Dentalhygiene-Leistungen bis zu einem jährlichen Höchstbetrag vorgesehen.
<customer>: Wie hoch ist der?
<agent>: Maximal 150 Franken pro Jahr.
<customer>: Das ist besser als nichts. Muss die Dentalhygienikerin speziell anerkannt sein?
<agent>: Ja, sie sollte bei einem anerkannten Berufsverband registriert sein. Das steht normalerweise auf der Rechnung.
<customer>: Gut, dann achte ich darauf.
<agent>: Reichen Sie uns die Rechnung einfach ein, und wir prüfen die Beteiligung.
<customer>: Alles klar, danke.
<agent>: Sehr gern, Herr Baumann.""",
        "topics": ["7"],
        "summary": "Customer asks about insurance contribution to professional teeth cleaning. There is an annual contribution provided the provider is recognized."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Berger. I want to ask a question about my roadside assistance.
<agent>: Hello Mr. Berger, this is Yann Morel. How can I help?
<customer>: If I'm traveling with a rental car, am I covered by my roadside assistance?
<agent>: In your policy PH-1780-E5, the coverage refers to your own vehicle with the registered license plate.
<customer>: So no?
<agent>: Exactly, your roadside assistance doesn't apply to a rental car. Most rental car providers have their own assistance services.
<customer>: Good to know. Then I need to look more carefully there.
<agent>: That's definitely recommended.
<customer>: Thanks for the clear answer.
<agent>: Very gladly, Mr. Berger.""",
        "topics": ["8"],
        "summary": "Customer inquires whether his roadside assistance also applies to rental cars. The coverage is vehicle-related and doesn't apply to rental vehicles."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I have a longer question about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. Tell me what concerns you.
<customer>: I recently renovated quite a bit and bought new appliances. I'm afraid I've overlooked something important.
<agent>: Then let's go through this systematically. Your policy HR-7227-U5 is currently issued for 70,000 francs household contents.
<customer>: That was before the renovations.
<agent>: Exactly. We could check it in five steps:
<agent>: First: We roughly record the value of your new furniture and appliances.
<customer>: That's certainly 15,000 to 20,000 francs.
<agent>: Second: We look at whether there are special individual pieces like designer items or antiques that should be listed separately.
<customer>: An antique table would be there.
<agent>: Third: We check whether the location of your risk has changed, for example through a move or major structural changes.
<customer>: No, the apartment is the same.
<agent>: Fourth: We calculate an adjusted insurance sum so you're not underinsured.
<customer>: And fifth?
<agent>: Fifth: We decide together whether additional modules like extended elemental damage or glass breakage make sense.
<customer>: Good, that sounds like a plan. Can you summarize this in writing for me?
<agent>: Very gladly, I'll send you a summary and a proposal for the new insurance sum to dvorak@hotmail.com.
<customer>: Thanks, then I'll go through everything in peace.
<agent>: Perfect, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is concerned about underinsurance after renovations and new purchases. A structured 5-point plan for adjusting property insurance is agreed upon.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe nochmals eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Was möchten Sie wissen?
<customer>: Ich überlege mir, die Versicherung komplett zu wechseln. Können Sie mir sagen, wie lange meine Kündigungsfrist ist?
<agent>: In Ihrer Police FV-6623-H3 ist eine Kündigung jeweils auf das Ende der Versicherungsperiode mit dreimonatiger Frist vorgesehen.
<customer>: Das heisst, ich bin noch fast ein Jahr gebunden?
<agent>: Ausser bei einem Schadenfall oder einer Prämienänderung – dann gibt es ein ausserordentliches Kündigungsrecht.
<customer>: Hm. Dann warte ich wohl ab, was mit den Prämien nächstes Jahr passiert.
<agent>: Das ist eine Möglichkeit. Wenn Sie möchten, kann ich Ihre Police auf Optimierungspotenzial prüfen, damit ein Wechsel vielleicht gar nicht nötig ist.
<customer>: Nein danke, im Moment will ich nur die Frist wissen.
<agent>: In Ordnung, Herr Keller. Dann bleibt es bei den genannten drei Monaten vor Ablauf.""",
        "topics": ["10"],
        "summary": "Customer inquires about cancellation period of his vehicle insurance because he considers switching. He leaves it at the information for now."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Noch eine Frage zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Gerne, was möchten Sie wissen?
<customer>: Deckt meine Police auch den Verlust meines Laptops auf Reisen?
<agent>: Ich sehe in Ihrer Police RV-8954-C5 eine Gepäckversicherung, allerdings mit einem Höchstbetrag pro Einzelgegenstand.
<customer>: Und wie hoch ist der?
<agent>: 2'000 Franken pro Gegenstand.
<customer>: Mein Laptop war teurer.
<agent>: Dann wäre im Schadenfall der Ersatz auf diesen Höchstbetrag begrenzt. Es gibt die Möglichkeit, besonders wertvolle Gegenstände separat zu versichern.
<customer>: Das ist ja wieder kompliziert. Aber gut, dann weiss ich Bescheid.
<agent>: Wenn Sie möchten, kann ich Ihnen Informationen zu einer separaten Elektronikversicherung schicken.
<customer>: Schicken Sie es, entscheiden werde ich später.
<agent>: Sehr gern, an roth@gmail.com.""",
        "topics": ["11"],
        "summary": "Customer asks if her laptop is fully covered while traveling. Luggage insurance has a maximum amount per item; a separate electronics insurance is mentioned as an option."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Weber. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Herr Weber, hier ist Anna Meier von der Vaudoise. Womit kann ich Ihnen helfen?
<customer>: Ich bin gerade umgezogen und frage mich, ob ich alle meine Policen aktualisieren muss.
<agent>: Das ist eine sehr wichtige Frage. Ein Umzug kann verschiedene Auswirkungen auf Ihre Versicherungen haben. Haben Sie Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 52-BH-3847-N2.
<agent>: Danke. Ich sehe hier eine Hausrat-, Privathaftpflicht- und Fahrzeugversicherung. Bei einem Umzug sollten wir mindestens die Adressen aktualisieren.
<customer>: Ändert sich dadurch auch die Prämie?
<agent>: Das kann durchaus sein, je nach Risikozone des neuen Wohnorts. Manchmal wird es günstiger, manchmal teurer.
<customer>: Können Sie das für mich prüfen und mir eine Übersicht schicken?
<agent>: Sehr gerne. Ich sende Ihnen eine Aufstellung aller notwendigen Änderungen an weber@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer inquires about updating his insurance policies after moving. The agent explains potential premium changes and offers to send a comprehensive overview."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Martin. J'ai l'impression qu'il me manque quelque chose dans mes assurances.
<agent>: Bonjour Madame Martin, ici Pascal Tremblay de Vaudoise. Qu'est-ce qui vous préoccupe?
<customer>: Je viens de commencer à travailler en freelance depuis la maison, et je me demande si mon équipement professionnel est couvert.
<agent>: C'est une excellente question. Votre police ménage standard couvre généralement l'équipement privé, mais pas nécessairement l'équipement professionnel.
<customer>: Et qu'est-ce que cela signifie concrètement? Mon ordinateur portable et mon matériel de bureau ne sont pas assurés?
<agent>: Cela dépend de la valeur et de l'usage. Pour un usage professionnel intensif, nous recommandons souvent une extension spéciale.
<customer>: Pouvez-vous me faire une offre pour cela? Je ne veux pas me retrouver sans protection.
<agent>: Bien sûr, je vous prépare une proposition pour une couverture équipement professionnel à domicile. Je vous l'envoie à martin@hotmail.com.""",
        "topics": ["2"],
        "summary": "Customer working as freelancer from home discovers potential coverage gap for professional equipment. Agent prepares special coverage proposal.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Thompson. I'm interested in expanding my insurance coverage with Vaudoise.
<agent>: Hello Mr. Thompson, this is Sarah Dürst from Vaudoise. What type of coverage are you looking for?
<customer>: I just bought a motorcycle and I need insurance for it. I already have car insurance with you.
<agent>: Excellent! Since you're already our customer, we can offer attractive package discounts. What type of motorcycle did you purchase?
<customer>: It's a touring bike, mainly for weekend trips and holidays.
<agent>: For touring bikes, I'd recommend comprehensive coverage including roadside assistance for longer trips. Would you like me to prepare a quote?
<customer>: Yes, please. But I want to see different options - basic and comprehensive coverage.
<agent>: Perfect. I'll prepare both variants and send them to thompson@gmail.com. You can then choose what fits your needs and budget best.""",
        "topics": ["3"],
        "summary": "Existing customer wants motorcycle insurance for his new touring bike. Agent prepares quotes for both basic and comprehensive coverage options.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Müller. Ich bin sehr unzufrieden mit der Bearbeitung meines Schadensfalls.
<agent>: Guten Tag Frau Müller, hier ist Marc Ducret. Es tut mir leid, dass Sie unzufrieden sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruchschaden, Referenz SV-7429-X1. Die Schadensregulierung zieht sich schon seit Wochen hin.
<agent>: Lassen Sie mich den Fall aufrufen... Ich sehe, dass noch zusätzliche Belege angefordert wurden. Haben Sie diese eingereicht?
<customer>: Ja, schon vor zwei Wochen! Aber seither höre ich nichts mehr. Das ist doch unmöglich.
<agent>: Sie haben recht, das ist zu lange. Ich sehe die Belege im System, aber sie wurden noch nicht bearbeitet. Das hätte schneller gehen müssen.
<customer>: Ich brauche das Geld dringend, um die Schäden zu reparieren. Wann kann ich endlich mit einer Entscheidung rechnen?
<agent>: Ich priorisiere Ihren Fall sofort und sorge dafür, dass die Bearbeitung bis spätestens übermorgen abgeschlossen ist. Sie erhalten eine schriftliche Bestätigung.""",
        "topics": ["4"],
        "summary": "Customer frustrated with delayed burglary claim processing despite submitting required documents weeks ago. Agent prioritizes the case for immediate completion."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Dubois. J'appelle pour suivre mon dossier sinistre.
<agent>: Bonjour Monsieur Dubois, ici Luca Steiner de Vaudoise. Quel est le numéro de référence?
<customer>: SN-8856-P4. Il s'agit des dégâts de grêle sur ma voiture.
<agent>: Je vois votre dossier. L'expert a terminé son évaluation et l'offre de règlement a été préparée.
<customer>: Et pourquoi ne l'ai-je pas encore reçue?
<agent>: Elle devait vous être envoyée hier. Permettez-moi de vérifier... Il semble y avoir eu un retard dans l'envoi postal.
<customer>: C'est toujours pareil avec vous. On doit constamment relancer.
<agent>: Je comprends votre frustration. Je vous envoie immédiatement l'offre par email et je vérifie que le courrier soit aussi expédié aujourd'hui.
<customer>: Faites donc cela. Et j'espère que le montant est correct cette fois.
<agent>: L'expert a évalué tous les dommages visibles. Si vous n'êtes pas d'accord, nous pouvons discuter d'une contre-expertise.""",
        "topics": ["5"],
        "summary": "Customer follows up on hail damage claim. Settlement offer was delayed in postal delivery, agent sends it immediately by email."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Johnson. I have a question about my premium payment.
<agent>: Good morning Mrs. Johnson, this is Nora Widmer from Vaudoise. How can I assist you?
<customer>: I received a bill that seems much higher than usual. I'm wondering if there's been a mistake.
<agent>: Let me check your account. Could you provide me with your policy number?
<customer>: It's PZ-4712-M9.
<agent>: Thank you. I see there was indeed a premium adjustment due to a claim you made last year, which affected your no-claims bonus.
<customer>: But I thought my bonus protection would prevent that?
<agent>: Your bonus protection covers one claim per year, but you had two claims in the same period, so the second one affected your premium.
<customer>: Nobody told me about this! I would have handled the smaller claim myself if I had known.
<agent>: I understand your concern. Let me send you a detailed breakdown showing how your premium was calculated, so you can see exactly what happened.""",
        "topics": ["6"],
        "summary": "Customer questions higher premium bill. Agent explains impact of multiple claims on no-claims bonus and offers detailed calculation breakdown."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Schmidt. Ich habe Fragen zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Schmidt, hier ist Anna Meier. Womit kann ich Ihnen helfen?
<customer>: Mein Physiotherapeut hat mir eine längere Behandlung empfohlen, und ich möchte wissen, was übernommen wird.
<agent>: Schauen wir in Ihre Police GS-5578-K2. Sie haben eine Zusatzversicherung mit Physiotherapie-Deckung.
<customer>: Gibt es eine Begrenzung der Anzahl Sitzungen?
<agent>: Pro Jahr sind 30 Sitzungen gedeckt, vorausgesetzt sie sind ärztlich verordnet.
<customer>: Mein Arzt empfiehlt 35 Sitzungen. Was passiert mit den zusätzlichen fünf?
<agent>: Die können über die Grundversicherung laufen oder Sie zahlen sie selbst. Ich empfehle, zuerst die Kostengutsprache für alle 35 Sitzungen zu beantragen.
<customer>: Können Sie mir die nötigen Formulare schicken?
<agent>: Gerne. Ich sende Ihnen alle Unterlagen an schmidt@gmail.com.""",
        "topics": ["7"],
        "summary": "Customer inquires about physiotherapy coverage limits. Agent explains 30 sessions are covered and helps with authorization process for additional sessions."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Petit. Mon auto est tombée en panne sur l'autoroute.
<agent>: Bonjour Madame Petit, ici Yann Morel de l'assistance Vaudoise. Êtes-vous en sécurité?
<customer>: Oui, je suis sur la bande d'arrêt d'urgence avec les feux de détresse allumés.
<agent>: Parfait. Où vous trouvez-vous exactement?
<customer>: Sur l'A1 direction Genève, juste après la sortie de Morges.
<agent>: Votre numéro de police est PH-9341-R7, c'est bien cela?
<customer>: Oui, c'est correct. Le moteur s'est arrêté d'un coup et ne redémarre plus.
<agent>: J'organise immédiatement un dépanneur. Il devrait arriver dans 30 à 40 minutes maximum.
<customer>: Et si la réparation n'est pas possible sur place?
<agent>: Alors on remorque votre véhicule vers un garage partenaire. Les frais sont couverts par votre assistance routière.
<customer>: Parfait, merci. J'attends alors le dépanneur.
<agent>: Il vous appellera quelques minutes avant d'arriver, Madame Petit.""",
        "topics": ["8"],
        "summary": "Customer's car breaks down on highway. Roadside assistance is dispatched with full coverage for towing and repair services."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Williams. I have a question about my property insurance.
<agent>: Good afternoon Mr. Williams, this is Pascal Tremblay from Vaudoise. What can I help you with?
<customer>: We're planning to install solar panels on our roof. Does this affect our property insurance?
<agent>: That's a great question. Solar panel installations can indeed impact your coverage. Let me check your policy HR-6684-L5.
<customer>: Do I need to inform you before the installation?
<agent>: Yes, it's important to notify us as it increases the value of your property and changes the risk profile slightly.
<customer>: Will this increase my premium significantly?
<agent>: Usually the increase is minimal because solar panels are well-secured installations. But the coverage increase protects your investment.
<customer>: That makes sense. What information do you need from me?
<agent>: I'll send you a simple form to complete with installation details and value. Then we can adjust your policy accordingly.""",
        "topics": ["9"],
        "summary": "Customer planning solar panel installation asks about property insurance impact. Agent explains notification requirements and minimal premium increase.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Hofmann. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Frau Hofmann, hier ist Sarah Dürst. Worum geht es?
<customer>: Meine Tochter hat gerade den Führerschein gemacht. Kann ich sie in meine Versicherung aufnehmen?
<agent>: Ja, das ist möglich. Allerdings wird sich die Prämie erhöhen, da Fahranfänger ein höheres Risiko darstellen.
<customer>: Um wie viel ungefähr?
<agent>: Das hängt vom Alter und anderen Faktoren ab. Für Ihre Police FV-7823-D6 würde ich schätzen, etwa 40-60% Aufschlag.
<customer>: Das ist aber teuer! Gibt es Alternativen?
<agent>: Wir könnten eine separate Police für Ihre Tochter eröffnen oder schauen, ob es günstigere Fahranfänger-Programme gibt.
<customer>: Schicken Sie mir bitte beide Varianten zur Ansicht.
<agent>: Sehr gerne, ich erstelle Ihnen eine Vergleichsrechnung und sende sie an hofmann@gmail.com.""",
        "topics": ["10"],
        "summary": "Customer wants to add newly licensed daughter to car insurance. Agent explains premium increase and offers comparison between adding to existing policy vs separate coverage."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Brown. I'm calling about my travel insurance.
<agent>: Hello Ms. Brown, this is Luca Steiner from Vaudoise. How can I help you?
<customer>: I'm planning a ski trip to the Alps next month. Does my travel insurance cover winter sports?
<agent>: Let me check your policy RV-1247-Q3... Yes, you have winter sports coverage included, but with certain conditions.
<customer>: What kind of conditions?
<agent>: The coverage applies to marked ski slopes and recognized winter sports areas. Off-piste skiing requires additional coverage.
<customer>: I'm only planning to ski on regular slopes. What about ski equipment?
<agent>: Your policy covers ski equipment up to 1,500 francs per person against theft or damage.
<customer>: That should be sufficient. Do I need to do anything special before the trip?
<agent>: No special preparation needed. Just make sure to keep receipts for any equipment rentals or purchases for potential claims.""",
        "topics": ["11"],
        "summary": "Customer confirms travel insurance coverage for upcoming ski trip. Agent explains winter sports coverage conditions and equipment protection limits."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Zimmermann. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Zimmermann, hier ist Marc Ducret. Wie kann ich Ihnen helfen?
<customer>: Ich habe geheiratet und möchte meine Frau als Begünstigte eintragen lassen.
<agent>: Herzlichen Glückwunsch zur Hochzeit! Das können wir gerne anpassen. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-8834-F7.
<agent>: Danke. Möchten Sie Ihre Frau als alleinige Begünstigte eintragen oder prozentual aufteilen?
<customer>: Als alleinige Begünstigte. Gibt es dabei etwas zu beachten?
<agent>: Bei einer Änderung der Begünstigung empfehlen wir auch zu prüfen, ob die Versicherungssumme noch angemessen ist.
<customer>: Das ist ein guter Punkt. Können Sie mir eine Einschätzung geben?
<agent>: Gerne. Ich sende Ihnen das Änderungsformular und eine Bedarfsanalyse für die Versicherungssumme an zimmermann@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to update life insurance beneficiary after marriage. Agent processes change and offers to review adequacy of insurance amount."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Leroy. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Madame Leroy, ici Anna Meier de Vaudoise. Que puis-je faire pour vous?
<customer>: J'ai hérité de bijoux de famille et je voudrais savoir s'ils sont automatiquement couverts.
<agent>: Les nouveaux objets de valeur ne sont pas automatiquement couverts. Il faut les déclarer et les faire évaluer.
<customer>: Comment procède-t-on pour l'évaluation?
<agent>: Vous devez faire appel à un expert bijoutier agréé qui établira une estimation officielle de la valeur.
<customer>: Et cela coûte cher?
<agent>: L'expertise coûte généralement entre 100 et 200 francs selon la complexité, mais c'est indispensable pour la couverture.
<customer>: D'accord. Pouvez-vous me donner les coordonnées d'experts agréés?
<agent>: Bien sûr, je vous envoie une liste d'experts dans votre région à leroy@gmail.com.""",
        "topics": ["13"],
        "summary": "Customer inherited family jewelry and asks about insurance coverage. Agent explains evaluation requirement by certified expert and provides expert list.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Wagner. Ich habe eine allgemeine Frage zu Vaudoise.
<agent>: Guten Tag Frau Wagner, hier ist Pascal Tremblay. Womit kann ich Ihnen behilflich sein?
<customer>: Ich überlege, alle meine Versicherungen bei einem Anbieter zu bündeln. Welche Vorteile bietet das?
<agent>: Eine Bündelung bringt mehrere Vorteile: Rabatte, einfachere Verwaltung und einen zentralen Ansprechpartner.
<customer>: Wie hoch sind die Rabatte normalerweise?
<agent>: Je nach Produktkombination können Sie zwischen 5 und 15 Prozent auf die Gesamtprämie sparen.
<customer>: Das klingt interessant. Ich habe derzeit Auto-, Hausrat- und Haftpflichtversicherung bei verschiedenen Anbietern.
<agent>: Das wären perfekte Kandidaten für eine Bündelung. Soll ich Ihnen eine unverbindliche Vergleichsrechnung erstellen?
<customer>: Ja, gerne. Aber ohne Verkaufsdruck bitte.
<agent>: Selbstverständlich. Sie erhalten nur Zahlen und Fakten zur eigenen Entscheidung. Ich sende die Berechnung an wagner@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance policies with Vaudoise. Agent explains benefits including discounts and offers comparison calculation."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Davis. I think I might have a gap in my insurance coverage.
<agent>: Hello Mr. Davis, this is Nora Widmer from Vaudoise. What makes you think there might be a gap?
<customer>: I started a small consulting business from home and I'm not sure if my professional liability is covered.
<agent>: That's an important concern. Personal liability insurance typically doesn't cover professional activities. Let me check your current coverage.
<customer>: My policy number is UD-5591-H8.
<agent>: I see you have personal liability but no professional liability insurance. For consulting work, you'd need a separate business liability policy.
<customer>: I was afraid of that. How urgent is this?
<agent>: Very urgent. If a client makes a claim against your consulting services, you wouldn't be protected without proper coverage.
<customer>: Can you prepare a quote for professional liability insurance?
<agent>: Absolutely. I'll prepare a quote specifically for consulting services and send it to davis@hotmail.com today.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for new consulting business. Personal liability doesn't cover professional activities, so separate business liability insurance is needed urgently."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Becker. Ich interessiere mich für eine neue Versicherung.
<agent>: Guten Tag Herr Becker, hier ist Sarah Dürst von der Vaudoise. Welche Art von Versicherung schwebt Ihnen vor?
<customer>: Ich kaufe ein Wohnmobil für den Ruhestand und brauche dafür eine passende Versicherung.
<agent>: Glückwunsch zum neuen Wohnmobil! Dafür gibt es spezielle Campingfahrzeug-Versicherungen mit erweiterten Leistungen.
<customer>: Was ist denn anders als bei einer normalen Fahrzeugversicherung?
<agent>: Zum Beispiel Campingzubehör-Versicherung, erweiterte Pannenhilfe in ganz Europa und Schutz bei längeren Standzeiten.
<customer>: Das klingt sinnvoll. Ich plane längere Reisen durch Europa.
<agent>: Dann ist eine umfassende Europa-Deckung besonders wichtig. Soll ich Ihnen verschiedene Deckungsoptionen zusammenstellen?
<customer>: Ja, bitte. Schicken Sie mir eine detaillierte Offerte mit verschiedenen Varianten.
<agent>: Sehr gerne. Ich erstelle Ihnen passende Angebote für Ihr Wohnmobil und sende sie an becker@gmail.com.""",
        "topics": ["3"],
        "summary": "Customer needs insurance for new motorhome for retirement travels. Agent explains specialized camping vehicle insurance with European coverage options."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Moreau. Je suis mécontent du règlement de mon sinistre.
<agent>: Bonjour Monsieur Moreau, ici Marc Ducret. Je suis désolé d'apprendre votre mécontentement. De quel sinistre s'agit-il?
<customer>: Dégâts d'eau dans ma cave, référence SV-2847-K9. Vous refusez une partie des dommages.
<agent>: Laissez-moi consulter le dossier... Je vois qu'une partie a été classée comme dommages préexistants.
<customer>: C'est ridicule! L'eau venait de la canalisation du voisin, pas de chez moi.
<agent>: Je comprends votre position. L'expert a constaté que certains dégâts étaient antérieurs à la fuite du voisin.
<customer>: Je ne peux pas accepter cela. Je veux une contre-expertise.
<agent>: C'est votre droit. Nous pouvons organiser une seconde expertise par un expert indépendant.
<customer>: Faites-le. Et cette fois, je veux être présent lors de l'inspection.
<agent>: Bien sûr, vous serez informé de tous les rendez-vous. Je lance la procédure immédiatement.""",
        "topics": ["4"],
        "summary": "Customer disputes water damage claim settlement where part was classified as pre-existing damage. Second independent expert evaluation is requested."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Taylor. I'm calling for an update on my claim.
<agent>: Good afternoon Mrs. Taylor, this is Luca Steiner from Vaudoise. What's your claim reference number?
<customer>: SN-3765-Q1. It's for the storm damage to my garden shed.
<agent>: Let me check... I see that the adjuster's report was completed and approved yesterday.
<customer>: Finally! When will I receive the settlement?
<agent>: The payment has been processed and should reach your account within 2-3 business days.
<customer>: Great. Will you also cover the cleanup costs for the debris?
<agent>: Yes, the cleanup costs are included in the settlement amount as they were part of the original damage assessment.
<customer>: Perfect. I was worried I'd have to pay for that separately.
<agent>: No, everything is covered as agreed. You'll receive a detailed settlement statement by email today.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on storm damage claim. Settlement including cleanup costs has been processed and will arrive within days."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Fischer. Ich habe eine Frage zu meiner Prämienrechnung.
<agent>: Guten Tag Herr Fischer, hier ist Anna Meier von der Vaudoise. Was ist unklar bei Ihrer Rechnung?
<customer>: Ich zahle seit Jahren pünktlich, aber bekomme nie einen Rabatt für treue Kunden.
<agent>: Lassen Sie mich Ihre Police PZ-6739-N4 prüfen... Sie haben bereits den maximalen Schadenfreiheitsrabatt.
<customer>: Aber andere Versicherer bieten zusätzliche Treueboni an.
<agent>: Das stimmt. Wir haben andere Vorteile wie kostenlose Serviceleistungen und bevorzugte Schadensbearbeitung für langjährige Kunden.
<customer>: Das ist mir nicht bekannt. Können Sie mir diese Leistungen auflisten?
<agent>: Gerne. Ich sende Ihnen eine Übersicht aller Zusatzleistungen, die Sie als Bestandskunde erhalten.
<customer>: Das wäre hilfreich. Vielleicht übersehe ich ja etwas.
<agent>: Ich bin sicher, da sind einige Leistungen dabei, die Sie noch nicht kannten. Die Übersicht geht an fischer@gmail.com.""",
        "topics": ["6"],
        "summary": "Long-term customer asks about loyalty discounts. Agent explains existing maximum discount and additional customer benefits for loyal clients."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Girard. J'ai des questions sur mes prestations santé.
<agent>: Bonjour Madame Girard, ici Nora Widmer. En quoi puis-je vous aider?
<customer>: Mon médecin m'a prescrit des séances de naturopathie. Est-ce que c'est couvert?
<agent>: Laissez-moi vérifier votre police GS-4493-T8... Vous avez une couverture médecines alternatives avec certaines conditions.
<customer>: Quelles conditions exactement?
<agent>: Le praticien doit être reconnu par l'ASCA ou le RME, et il y a un plafond annuel de 1000 francs.
<customer>: Et comment savoir si mon naturopathe est reconnu?
<agent>: Vous pouvez vérifier sur les sites web ASCA ou RME, ou simplement demander à votre praticien ses certifications.
<customer>: D'accord. Et si je dépasse les 1000 francs?
<agent>: Alors les frais supplémentaires seraient à votre charge. Je vous envoie la liste des praticiens reconnus dans votre région pour référence.""",
        "topics": ["7"],
        "summary": "Customer inquires about naturopathy coverage. Agent explains recognition requirements and annual limits for alternative medicine practitioners."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Anderson. I need emergency roadside assistance.
<agent>: Hello Mr. Anderson, this is Yann Morel from Vaudoise assistance. Are you in a safe location?
<customer>: Yes, I'm in a parking lot. My car won't start and I have an important meeting in an hour.
<agent>: I understand the urgency. What's your location and policy number?
<customer>: I'm at the shopping center in Lausanne, policy PH-7741-S3.
<agent>: Perfect, I can dispatch a technician immediately. They should arrive within 20-25 minutes.
<customer>: What if they can't fix it on site?
<agent>: If it can't be repaired, we can provide a replacement vehicle so you can make your meeting.
<customer>: You have replacement cars available?
<agent>: Yes, your policy includes replacement vehicle service for mechanical breakdowns. The technician will arrange it if needed.
<customer>: That's a relief. Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs urgent roadside assistance before important meeting. Quick dispatch arranged with replacement vehicle option if repair isn't possible."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Koch. Ich habe eine Frage zur Gebäudeversicherung.
<agent>: Guten Tag Frau Koch, hier ist Pascal Tremblay von der Vaudoise. Wobei kann ich helfen?
<customer>: Wir haben einen Swimming Pool bauen lassen. Muss das in der Versicherung angemeldet werden?
<agent>: Das ist eine wichtige Frage. Ein Pool erhöht den Gebäudewert und sollte definitiv gemeldet werden.
<customer>: Wird dadurch die Prämie viel teurer?
<agent>: Die Erhöhung ist normalerweise moderat, da Pools fest installiert und gegen die meisten Risiken gut geschützt sind.
<customer>: Was ist mit der Haftpflicht? Wenn jemand im Pool verunglückt?
<agent>: Das wäre über Ihre Privathaftpflichtversicherung gedeckt, vorausgesetzt Sie haben den Pool ordnungsgemäß gesichert.
<customer>: Können Sie beide Policen entsprechend anpassen?
<agent>: Gerne. Ich erstelle Ihnen die Anpassungen und sende sie zur Prüfung an koch@gmail.com.""",
        "topics": ["9"],
        "summary": "Customer reports new swimming pool construction. Agent explains building insurance adjustment and liability coverage requirements."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Bernard. Ma voiture a été volée cette nuit.
<agent>: Bonjour Monsieur Bernard, ici Sarah Dürst de Vaudoise. Je suis désolée d'apprendre cela. Avez-vous déjà contacté la police?
<customer>: Oui, j'ai déposé plainte ce matin. Le numéro de plainte est 2024-445-891.
<agent>: Parfait. Votre numéro de police est FV-5529-J6, c'est bien cela?
<customer>: Oui. Qu'est-ce que je dois faire maintenant?
<agent>: Je vais ouvrir un dossier sinistre immédiatement. Vous devez nous envoyer une copie de la plainte et nous donner tous les détails du vol.
<customer>: La voiture était fermée à clé devant chez moi. Il n'y avait rien d'anormal.
<agent>: D'accord. Avez-vous encore tous les clés en votre possession?
<customer>: Oui, toutes les clés étaient à la maison. Comment ça se passe pour le remboursement?
<agent>: Nous attendons d'abord que la police termine son enquête, puis nous procédons selon la valeur actuelle de votre véhicule.""",
        "topics": ["10"],
        "summary": "Customer reports car theft that occurred overnight. Agent opens claim file and explains process including police investigation and current value assessment."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Ms. Wilson. I have a question about my travel insurance.
<agent>: Good afternoon Ms. Wilson, this is Marc Ducret from Vaudoise. What would you like to know?
<customer>: I'm pregnant and wondering if this affects my travel insurance for an upcoming trip.
<agent>: Congratulations! Pregnancy does have some implications for travel insurance. Let me check your policy RV-8822-D7.
<customer>: I'm in my second trimester and planning to travel to Italy next month.
<agent>: For pregnancy-related coverage, there are specific conditions. Normal pregnancy isn't considered an illness, but complications could be covered.
<customer>: What if I need medical attention while abroad?
<agent>: Emergency medical care is covered, but routine pregnancy check-ups during travel are not included in standard coverage.
<customer>: Should I consider additional coverage?
<agent>: I'd recommend discussing with your doctor first about travel safety, then we can assess if additional pregnancy-related coverage would be beneficial.""",
        "topics": ["11"],
        "summary": "Pregnant customer inquires about travel insurance coverage. Agent explains emergency vs routine care coverage and suggests medical consultation first."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Richter. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Richter, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich bin arbeitslos geworden und kann mir die Prämien nicht mehr leisten. Was sind meine Optionen?
<agent>: Das tut mir leid zu hören. Es gibt mehrere Möglichkeiten: Prämienbefreiung, Reduktion der Versicherungssumme oder temporäre Aussetzung.
<customer>: Was bedeutet Prämienbefreiung genau?
<agent>: Bei nachgewiesener Arbeitslosigkeit können wir die Prämienzahlung für bis zu 12 Monate aussetzen, ohne dass der Vertrag verfällt.
<customer>: Das wäre ideal. Welche Unterlagen brauchen Sie?
<agent>: Eine Bescheinigung des RAV und einen Nachweis über das Arbeitslosengeld. Der Schutz bleibt während dieser Zeit bestehen.
<customer>: Perfekt. Wo kann ich diese Unterlagen einreichen?
<agent>: Ich sende Ihnen das entsprechende Formular und die Anweisungen an richter@gmail.com.""",
        "topics": ["12"],
        "summary": "Unemployed customer can't afford life insurance premiums. Agent explains premium waiver option for unemployment with continued coverage.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. Roberts. I have a question about my valuables insurance.
<agent>: Hello Mrs. Roberts, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm going on vacation and want to take some jewelry with me. Are they covered while traveling?
<agent>: Your valuables policy WV-7734-X2 includes worldwide coverage, but with certain security requirements while traveling.
<customer>: What kind of security requirements?
<agent>: Items should not be left unattended in vehicles, and hotel safes should be used when available. There are also coverage limits per item.
<customer>: What if the hotel doesn't have a safe?
<agent>: Then you should keep valuable items with you at all times or consider leaving very expensive pieces at home for this trip.
<customer>: That makes sense. Is there anything else I should know?
<agent>: Take photos of the jewelry before traveling and keep receipts. This helps with any potential claims.""",
        "topics": ["13"],
        "summary": "Customer asks about jewelry coverage while traveling. Agent explains worldwide coverage with security requirements and documentation recommendations."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Neumann. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Frau Neumann, hier ist Pascal Tremblay. Was beschäftigt Sie?
<customer>: Meine Nachbarin hatte einen Wasserschaden und war wochenlang ohne Heizung. Bin ich dagegen versichert?
<agent>: Das ist eine wichtige Überlegung. Schauen wir in Ihre Hausratversicherung HR-9966-L1, ob zusätzliche Lebenshaltungskosten gedeckt sind.
<customer>: Was sind zusätzliche Lebenshaltungskosten?
<agent>: Wenn Ihre Wohnung unbewohnbar wird, zahlen wir Hotelkosten oder Miete für eine Ersatzwohnung für eine begrenzte Zeit.
<customer>: Wie lange ist diese begrenzte Zeit?
<agent>: In Ihrer Police sind bis zu 12 Monate gedeckt, je nach Umfang der Schäden und Reparaturdauer.
<customer>: Das beruhigt mich. Muss ich bestimmte Hotels wählen?
<agent>: Nein, aber die Kosten müssen angemessen sein. Wir erstatten bis zur Höhe Ihrer normalen Wohnkosten plus einem Aufschlag.
<customer>: Gut zu wissen. Danke für die Erklärung.""",
        "topics": ["1"],
        "summary": "Customer asks about coverage for alternative accommodation after hearing neighbor's water damage story. Agent explains additional living costs coverage terms."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Fabre. Je pense avoir un besoin d'assurance non couvert.
<agent>: Bonjour Monsieur Fabre, ici Sarah Dürst. Qu'est-ce qui vous préoccupe?
<customer>: Je fais de la photographie professionnelle et mon équipement coûte très cher. Mon assurance ménage ne suffit pas.
<agent>: Effectivement, l'équipement professionnel nécessite souvent une couverture spécialisée. Quelle est la valeur approximative?
<customer>: Environ 25'000 francs en appareils photos, objectifs et équipement d'éclairage.
<agent>: Pour cette valeur, nous recommandons une assurance équipement professionnel avec couverture mondiale.
<customer>: Mondiale? Pourquoi?
<agent>: Pour un photographe, l'équipement voyage beaucoup. Il faut une protection contre le vol, les dommages et la perte, même à l'étranger.
<customer>: Cela me semble logique. Pouvez-vous me faire une offre?
<agent>: Bien sûr, je vous prépare une proposition pour assurance équipement professionnel photographique. Je l'envoie à fabre@gmail.com.""",
        "topics": ["2"],
        "summary": "Professional photographer needs specialized equipment insurance beyond standard household coverage. Agent prepares worldwide professional equipment proposal."
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Clarke. I'm interested in business insurance for my new company.
<agent>: Good morning Mr. Clarke, this is Marc Ducret from Vaudoise. Congratulations on your new business! What type of company are you starting?
<customer>: It's a small IT consulting firm. I'll be working mostly with corporate clients on software projects.
<agent>: For IT consulting, you'll need professional liability insurance, general liability, and possibly cyber liability coverage.
<customer>: Cyber liability? What's that for?
<agent>: It protects against data breaches, cyber attacks, and privacy violations. Very important for IT companies handling client data.
<customer>: That makes sense. How much does this typically cost for a small firm?
<agent>: For a startup IT consulting firm, we're typically looking at 1,500 to 3,000 francs annually for a comprehensive package.
<customer>: That seems reasonable. Can you prepare a detailed quote?
<agent>: Absolutely. I'll create a tailored business insurance package for your IT consulting firm and send it to clarke@gmail.com.""",
        "topics": ["3"],
        "summary": "Entrepreneur needs business insurance for new IT consulting firm. Agent explains professional, general, and cyber liability coverage needs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Weber. Ich bin extrem verärgert über die Schadensbearbeitung.
<agent>: Guten Tag Frau Weber, hier ist Luca Steiner. Es tut mir leid zu hören, dass Sie verärgert sind. Was ist passiert?
<customer>: Sturmschaden am Dach, Referenz SV-5641-M2. Die Reparatur wurde abgelehnt wegen angeblicher Vorschäden.
<agent>: Lassen Sie mich den Fall prüfen... Ich sehe, dass der Gutachter Altersschwäche der Dachziegel festgestellt hat.
<customer>: Das Dach ist erst fünf Jahre alt! Das ist doch kein Alter.
<agent>: Sie haben recht, das ist sehr jung für ein Dach. Haben Sie noch Garantieunterlagen vom Dachdecker?
<customer>: Natürlich! Die habe ich auch schon eingereicht, aber niemand hat darauf reagiert.
<agent>: Das hätte beachtet werden müssen. Ich lasse den Fall von unserem Bauschadenexperten neu bewerten.
<customer>: Endlich mal jemand, der zuhört! Wann kann ich mit einer Antwort rechnen?
<agent>: Bis Ende der Woche haben Sie eine neue Einschätzung. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["4"],
        "summary": "Customer frustrated about roof damage claim rejection due to alleged pre-existing damage on 5-year-old roof. Case referred to construction damage expert for reevaluation."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Rousseau. Je voudrais un point sur mon sinistre.
<agent>: Bonjour Madame Rousseau, ici Anna Meier de Vaudoise. Quel est votre numéro de référence?
<customer>: SN-7788-V5. Il s'agit du cambriolage de mon appartement il y a trois semaines.
<agent>: Je vois votre dossier. L'enquête de police est terminée et nous avons reçu le rapport officiel.
<customer>: Parfait. Et maintenant?
<agent>: Nous finalisons l'inventaire des objets volés. Avez-vous d'autres preuves d'achat à nous envoyer?
<customer>: Non, je vous ai tout transmis. Quand vais-je être indemnisée?
<agent>: Le règlement sera effectué dans les 5 jours ouvrables. Vous recevrez d'abord un décompte détaillé.
<customer>: Très bien. Y aura-t-il une franchise à déduire?
<agent>: Oui, votre police prévoit une franchise de 500 francs pour les cambriolages.
<customer>: D'accord, je m'y attendais. Merci pour ces nouvelles rassurantes.""",
        "topics": ["5"],
        "summary": "Customer gets positive update on burglary claim. Police investigation complete, settlement will be processed within 5 business days with standard deductible."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Turner. I have a billing question.
<agent>: Hello Mr. Turner, this is Pascal Tremblay from Vaudoise. What's your billing concern?
<customer>: I switched to annual payments instead of quarterly, but I was charged a processing fee.
<agent>: Let me check your account PZ-8844-R7... I see the payment frequency change and the associated fee.
<customer>: I wasn't told there would be a fee for this change.
<agent>: You're right, that should have been communicated clearly. The fee is typically waived for voluntary changes to less frequent payments.
<customer>: So the fee shouldn't have been charged?
<agent>: Correct. I'll reverse the processing fee and it should appear as a credit on your next statement.
<customer>: Thank you. Will this happen again if I make other changes?
<agent>: No, changes that reduce our administrative costs, like yours, shouldn't incur fees. I'll make sure this is noted in your file.""",
        "topics": ["6"],
        "summary": "Customer charged unexpected fee for switching to annual payments. Agent reverses fee and clarifies that beneficial payment changes shouldn't incur costs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Maurer. Ich habe Fragen zu Gesundheitsleistungen.
<agent>: Guten Tag Herr Maurer, hier ist Nora Widmer. Womit kann ich helfen?
<customer>: Mein Arzt hat mir Akupunktur verschrieben. Wird das übernommen?
<agent>: Schauen wir in Ihre Police GS-3377-B9... Sie haben eine Zusatzversicherung mit Komplementärmedizin-Deckung.
<customer>: Wie funktioniert die Kostenerstattung?
<agent>: Die Behandlung muss von einem anerkannten Therapeuten durchgeführt werden, dann erstatten wir 70% der Kosten.
<customer>: Bis zu welchem jährlichen Betrag?
<agent>: Ihr Jahresbudget für Komplementärmedizin beträgt 800 Francs.
<customer>: Und wie weiss ich, ob mein Therapeut anerkannt ist?
<agent>: Fragen Sie nach der ASCA- oder RME-Registrierung oder geben Sie mir die Praxisdaten, dann prüfe ich das für Sie.
<customer>: Die Praxis ist in Bern, Dr. Chen, Akupunkturzentrum Bern.
<agent>: Ich prüfe das und melde mich noch heute bei Ihnen zurück.""",
        "topics": ["7"],
        "summary": "Customer asks about acupuncture coverage. Agent explains 70% reimbursement with annual limit and offers to verify therapist recognition status."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Phillips. I need roadside assistance.
<agent>: Good afternoon Mrs. Phillips, this is Yann Morel from Vaudoise assistance. What's your situation?
<customer>: I have a flat tire and I don't have a spare. I'm on the highway near Bern.
<agent>: Are you in a safe location off the roadway?
<customer>: Yes, I'm in a rest area with my hazard lights on.
<agent>: Perfect. Your policy PH-2255-K8 includes tire service. I can send a mobile tire service to replace your flat tire.
<customer>: How long will that take?
<agent>: The tire service should reach you within 45 minutes. They'll have common tire sizes on the truck.
<customer>: What if they don't have my tire size?
<agent>: Then we'll tow you to the nearest tire shop and cover the costs. Your policy includes this service.
<customer>: Great, that takes the stress away. Thank you for the quick help.""",
        "topics": ["8"],
        "summary": "Customer has flat tire on highway with no spare. Mobile tire service dispatched with backup towing option if needed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Vogel. Es geht um meine Wohngebäudeversicherung.
<agent>: Guten Tag Herr Vogel, hier ist Sarah Dürst. Was kann ich für Sie tun?
<customer>: Wir planen einen Wintergarten anzubauen. Muss das versichert werden?
<agent>: Ja, Anbauten erhöhen die Gebäudeversicherungssumme und sollten gemeldet werden.
<customer>: Der Wintergarten kostet etwa 50.000 Franken. Wie stark steigt dadurch die Prämie?
<agent>: Bei Ihrer Police HR-4488-W6 würde das etwa 120-150 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist weniger als erwartet. Wann muss ich das melden?
<agent>: Idealerweise vor Baubeginn, spätestens bei Fertigstellung. So ist der Anbau von Anfang an mitversichert.
<customer>: Gibt es besondere Auflagen für Wintergärten?
<agent>: Meist nicht, solange er nach den Bauvorschriften errichtet wird. Senden Sie mir die Baupläne, dann prüfe ich das genauer.""",
        "topics": ["9"],
        "summary": "Customer planning winter garden addition asks about building insurance requirements. Agent explains coverage increase and timing for reporting construction."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Blanc. J'ai des questions sur mon assurance auto.
<agent>: Bonjour Madame Blanc, ici Marc Ducret de Vaudoise. Que voulez-vous savoir?
<customer>: Mon fils va bientôt avoir 18 ans et passer son permis. Comment l'assurer?
<agent>: Il y a plusieurs options: l'ajouter à votre police existante ou lui faire une police séparée.
<customer>: Qu'est-ce qui est le plus avantageux?
<agent>: Cela dépend de votre bonus actuel. L'ajouter peut être moins cher, mais risque d'affecter votre bonus en cas d'accident.
<customer>: Et avec une police séparée?
<agent>: Il commence avec un bonus jeune conducteur, mais vos polices restent indépendantes.
<customer>: Peut-être que c'est plus sûr. Pouvez-vous calculer les deux variantes?
<agent>: Bien sûr, je vous prépare une comparaison des coûts et avantages de chaque solution. Je l'envoie à blanc@gmail.com.""",
        "topics": ["10"],
        "summary": "Mother asks about insuring her soon-to-be 18-year-old son. Agent explains options of adding to existing policy vs separate coverage with pros and cons.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Green. I have a travel insurance question.
<agent>: Good morning Mr. Green, this is Luca Steiner from Vaudoise. What would you like to know?
<customer>: I'm planning a business trip that might extend into a vacation. Does my travel insurance cover both purposes?
<agent>: Let me check your policy RV-6655-F4... You have standard travel insurance which covers both business and leisure travel.
<customer>: What if the trip gets extended unexpectedly for business reasons?
<agent>: Extensions for business reasons are generally covered, but there's a maximum trip duration limit in your policy.
<customer>: What's my limit?
<agent>: Your policy covers trips up to 180 days. If you need longer coverage, we'd need to arrange extended travel insurance.
<customer>: That should be plenty. Is there anything special I need to do for combined business-leisure trips?
<agent>: No special requirements, the coverage is the same regardless of the purpose of your travel.""",
        "topics": ["11"],
        "summary": "Customer asks about travel insurance for combined business-leisure trip. Standard coverage applies to both purposes with 180-day maximum duration."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Lang. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Frau Lang, hier ist Anna Meier. Wie kann ich Ihnen helfen?
<customer>: Meine finanzielle Situation hat sich verbessert und ich möchte die Versicherungssumme erhöhen.
<agent>: Das freut mich für Sie! Schauen wir uns Ihre Police LV-7711-Q3 an. Um wie viel möchten Sie erhöhen?
<customer>: Von 150.000 auf 250.000 Franken.
<agent>: Das ist eine substanzielle Erhöhung. Dafür ist normalerweise eine neue Gesundheitsprüfung erforderlich.
<customer>: Auch wenn ich schon Kunde bin?
<agent>: Ja, bei Erhöhungen über 50.000 Franken ist eine Gesundheitsprüfung Standard, unabhängig von der bestehenden Kundenbeziehung.
<customer>: Wie läuft das ab?
<agent>: Zuerst füllen Sie einen Gesundheitsfragebogen aus, möglicherweise folgt dann eine ärztliche Untersuchung.
<customer>: Schicken Sie mir die Unterlagen zu. Ich bin gesund und mache mir keine Sorgen.
<agent>: Sehr gerne. Die Unterlagen für die Erhöhung gehen an lang@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to increase life insurance sum due to improved financial situation. Agent explains health examination requirements for substantial increases."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Stone. I have a question about my valuables insurance.
<agent>: Hello Mr. Stone, this is Pascal Tremblay from Vaudoise. How can I help you?
<customer>: I collect vintage watches and some have appreciated significantly in value. Should I update my coverage?
<agent>: Absolutely! Appreciated items should definitely be revalued for proper coverage. When was your last appraisal?
<customer>: About three years ago. Some pieces have doubled in value since then.
<agent>: Then an update is overdue. Underinsurance could result in reduced payouts in case of loss.
<customer>: What's the process for updating values?
<agent>: You'll need fresh appraisals from certified watch experts. We can provide a list of recognized appraisers.
<customer>: That makes sense. Will my premiums increase significantly?
<agent>: Premiums will adjust to reflect the new values, but it's better to pay slightly more for proper coverage than risk major losses.
<customer>: You're right. Please send me the appraiser list and update forms.""",
        "topics": ["13"],
        "summary": "Vintage watch collector needs to update valuables coverage after significant appreciation. Agent emphasizes importance of current appraisals and offers appraiser list.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Huber. Ich habe eine grundsätzliche Frage zu Versicherungen.
<agent>: Guten Tag Herr Huber, hier ist Sarah Dürst. Was beschäftigt Sie?
<customer>: Ich lebe seit kurzem allein nach der Scheidung und frage mich, welche Versicherungen ich wirklich brauche.
<agent>: Das ist eine wichtige Überprüfung nach einer Lebensveränderung. Welche Versicherungen haben Sie derzeit?
<customer>: Auto, Hausrat und Privathaftpflicht. Meine Ex-Frau hatte immer die Übersicht.
<agent>: Das ist eine solide Grundausstattung. Haben Sie Kinder oder Unterhaltsverpflichtungen?
<customer>: Zwei Kinder, ja. Ich zahle Unterhalt.
<agent>: Dann könnte eine Lebensversicherung sinnvoll sein, um die Unterhaltszahlungen abzusichern.
<customer>: Daran habe ich nicht gedacht. Können Sie mir eine Bedarfsanalyse machen?
<agent>: Gerne erstelle ich Ihnen eine individuelle Bedarfsanalyse basierend auf Ihrer neuen Lebenssituation.""",
        "topics": ["1"],
        "summary": "Recently divorced customer reviews insurance needs for new life situation with children and alimony obligations. Agent offers comprehensive needs analysis.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Dupont. Je crois avoir une lacune dans mes assurances.
<agent>: Bonjour Madame Dupont, ici Marc Ducret. Quelle lacune suspectez-vous?
<customer>: J'ai commencé à faire de la location Airbnb dans ma maison secondaire. Est-ce que c'est couvert?
<agent>: C'est une excellente question. La location courte durée n'est généralement pas couverte par l'assurance habitation standard.
<customer>: Qu'est-ce que cela signifie concrètement?
<agent>: En cas de dommages causés par des locataires Airbnb, votre assurance pourrait refuser la prise en charge.
<customer>: C'est embêtant! Que puis-je faire?
<agent>: Nous avons des extensions spéciales pour location courte durée qui couvrent ces risques spécifiques.
<customer>: Et pour la responsabilité civile si un locataire se blesse?
<agent>: Cela aussi nécessite une couverture étendue. Je vous prépare une offre complète pour activité Airbnb.
<customer>: Faites cela rapidement, j'ai déjà des réservations pour le mois prochain.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for Airbnb rental activity in secondary home. Standard home insurance doesn't cover short-term rentals; special extension needed urgently.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Harris. I'm interested in additional insurance products.
<agent>: Good afternoon Mrs. Harris, this is Nora Widmer from Vaudoise. What type of additional coverage interests you?
<customer>: I'm thinking about legal protection insurance. I've been having some disputes with contractors lately.
<agent>: Legal protection can be very valuable, especially if you frequently deal with service providers. What type of disputes are you facing?
<customer>: Mainly construction and renovation issues. Poor workmanship and contract disagreements.
<agent>: Legal protection insurance would cover consultation with lawyers and court costs for such disputes.
<customer>: Does it cover ongoing disputes or only new ones after the policy starts?
<agent>: Only disputes that arise after the policy effective date. Ongoing issues wouldn't be covered.
<customer>: That's fair. How much does legal protection typically cost?
<agent>: For comprehensive legal protection, you're looking at around 300-400 francs annually, depending on coverage limits.""",
        "topics": ["3"],
        "summary": "Customer interested in legal protection insurance due to contractor disputes. Agent explains coverage for future disputes only and provides cost estimates."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Keller. Ich bin wirklich sauer auf die Schadensregulierung.
<agent>: Guten Tag Frau Keller, hier ist Luca Steiner. Es tut mir leid, dass Sie verärgert sind. Was ist geschehen?
<customer>: Glasschaden am Auto, Referenz SV-9922-T7. Der Schaden wurde abgelehnt wegen angeblicher Manipulation.
<agent>: Das ist ein schwerwiegender Vorwurf. Lassen Sie mich den Fall genau prüfen.
<customer>: Ich habe einen Steinschlag gehabt, das ist alles! Warum sollte ich das manipulieren?
<agent>: Ich verstehe Ihre Verärgerung. Können Sie mir den Hergang nochmals schildern?
<customer>: Ich fuhr hinter einem Lastwagen, plötzlich Knall in der Scheibe. Ganz normal halt.
<agent>: Haben Sie Zeugen oder war jemand anders im Auto?
<customer>: Meine Nachbarin sass neben mir. Sie kann das bestätigen.
<agent>: Das ist wichtig. Ich lasse den Fall von einem anderen Sachbearbeiter neu bewerten und berücksichtige die Zeugenaussage.
<customer>: Endlich jemand, der mir glaubt! Wann höre ich etwas?""",
        "topics": ["4"],
        "summary": "Customer angry about glass damage claim rejection due to alleged manipulation. Agent reopens case with new adjuster and includes witness testimony."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Mitchell. I'm calling about my claim status.
<agent>: Hello Mr. Mitchell, this is Anna Meier from Vaudoise. What's your claim reference?
<customer>: SN-4433-L6. It's for water damage from a burst pipe last month.
<agent>: Let me check your file... I see the restoration work has been completed and final invoices received.
<customer>: Yes, everything's done. When can I expect final payment?
<agent>: The final payment has been approved and will be transferred to your account tomorrow morning.
<customer>: Excellent. Will there be any adjustment to the original estimate?
<agent>: Actually yes, the final amount is about 800 francs less than estimated because some damaged items could be repaired instead of replaced.
<customer>: That's good news. Will I receive a detailed final statement?
<agent>: Yes, you'll get a complete breakdown of all costs and payments by email today.
<customer>: Perfect. Thank you for the efficient handling of this claim.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on water damage claim. Final payment approved with costs lower than estimated due to successful repairs rather than replacements."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Graf. Ich verstehe meine Prämienrechnung nicht.
<agent>: Guten Tag Herr Graf, hier ist Pascal Tremblay. Was ist unklar an Ihrer Rechnung?
<customer>: Es gibt verschiedene Abzüge und Zuschläge, ich kenne mich nicht aus.
<agent>: Gerne erkläre ich Ihnen die Rechnung Schritt für Schritt. Haben Sie sie vor sich?
<customer>: Ja. Da steht etwas von einem Schadenfreiheitsrabatt und einem Selbstbehalt-Bonus.
<agent>: Der Schadenfreiheitsrabatt belohnt Sie dafür, dass Sie keine Schäden hatten. Je länger schadensfrei, desto höher der Rabatt.
<customer>: Und der Selbstbehalt-Bonus?
<agent>: Den erhalten Sie, weil Sie einen höheren Selbstbehalt gewählt haben. Das reduziert Ihre Grundprämie.
<customer>: Verstehe. Und warum ist dann noch ein Zuschlag da?
<agent>: Welcher Zuschlag genau? Können Sie mir die Zeile vorlesen?
<customer>: "Regionale Anpassung +15%".
<agent>: Das ist ein regionaler Zuschlag aufgrund höherer Schadenkosten in Ihrer Gegend. Der ist leider unvermeidlich.""",
        "topics": ["6"],
        "summary": "Customer confused about premium calculation details. Agent explains no-claims discount, deductible bonus, and regional adjustment factors step by step."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Leroy. J'ai des questions sur ma couverture santé.
<agent>: Bonjour Monsieur Leroy, ici Sarah Dürst. En quoi puis-je vous aider?
<customer>: Mon dentiste propose un nouveau traitement coûteux et je veux savoir ce qui est pris en charge.
<agent>: De quel type de traitement s'agit-il?
<customer>: Des implants dentaires. Cela coûte environ 8000 francs.
<agent>: Regardons votre police GS-6688-U7... Vous avez une couverture dentaire avec certaines limitations.
<customer>: Quelles limitations?
<agent>: Les implants sont couverts à hauteur de 75% maximum 5000 francs par an pour les traitements dentaires majeurs.
<customer>: Donc je recevrais 5000 francs maximum?
<agent>: Exactement. Et il faut d'abord obtenir une autorisation de coûts avant de commencer le traitement.
<customer>: Comment faire cette demande?
<agent>: Votre dentiste doit nous envoyer un plan de traitement détaillé avec devis. Nous évaluons ensuite la nécessité médicale.""",
        "topics": ["7"],
        "summary": "Customer asks about dental implant coverage. Policy covers 75% up to 5000 francs annually for major dental work with prior authorization required."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Cooper. I need emergency roadside assistance.
<agent>: Good morning Mrs. Cooper, this is Yann Morel from Vaudoise assistance. What's your emergency?
<customer>: My car battery is dead in a parking garage. I think I left the lights on overnight.
<agent>: That happens to everyone! Are you in a safe, accessible location for our service vehicle?
<customer>: Yes, it's a public parking garage with good access.
<customer>: Can you give me your exact location and policy number?
<agent>: I'm at the Westside shopping center in Bern, underground parking level 1. Policy PH-5577-N9.
<agent>: Perfect. I can dispatch a mobile battery service immediately. They'll have jump cables and replacement batteries if needed.
<customer>: How quickly can they get here?
<agent>: For parking garage locations, usually 15-20 minutes. They'll call you when they arrive at the entrance.
<customer>: Excellent service! Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs jump start for dead battery in shopping center parking garage. Mobile battery service dispatched with 15-20 minute response time."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Gross. Frage zur Gebäudeversicherung.
<agent>: Guten Tag Herr Gross, hier ist Marc Ducret. Womit kann ich helfen?
<customer>: Wir installieren eine Wärmepumpe. Ändert das etwas an der Versicherung?
<agent>: Eine Wärmepumpe ist eine wertvolle Gebäudeinstallation und sollte mitversichert werden.
<customer>: Die Anlage kostet 25.000 Franken. Um wie viel steigt die Prämie?
<agent>: Bei Ihrer Police HR-1199-X3 würde das etwa 60-80 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist moderat. Gibt es besondere Risiken bei Wärmepumpen?
<agent>: Hauptrisiken sind Frost-, Elektronik- und Vandalismusschäden. Letztere sind leider nicht selten.
<customer>: Vandalismusschäden? Bei einer Wärmepumpe?
<agent>: Ja, die Außengeräte werden leider manchmal mutwillig beschädigt. Deshalb ist eine umfassende Deckung wichtig.
<customer>: Dann sollten wir das auf jeden Fall machen. Schicken Sie mir die Unterlagen.""",
        "topics": ["9"],
        "summary": "Customer installing heat pump asks about building insurance implications. Agent explains coverage importance including vandalism protection for outdoor units."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Vincent. Question sur mon assurance véhicule.
<agent>: Bonjour Madame Vincent, ici Luca Steiner de Vaudoise. Que voulez-vous savoir?
<customer>: Je vais acheter une voiture électrique. Est-ce que cela change quelque chose à mon assurance?
<agent>: Les voitures électriques ont quelques spécificités. Elles nécessitent souvent une couverture étendue pour la batterie.
<customer>: Pourquoi la batterie spécifiquement?
<agent>: Les batteries coûtent très cher à remplacer et ont des risques particuliers comme la surchauffe ou les dégâts dus au sel de route.
<customer>: Et pour l'assistance routière?
<agent>: Nous recommandons une assistance étendue car les pannes électriques nécessitent des dépanneurs spécialisés.
<customer>: Cela va coûter beaucoup plus cher?
<agent>: Environ 10-15% de plus qu'une voiture classique, mais c'est justifié par les technologies spécifiques.
<customer>: D'accord. Préparez-moi une offre complète pour véhicule électrique.""",
        "topics": ["10"],
        "summary": "Customer buying electric vehicle asks about insurance differences. Agent explains battery coverage and specialized roadside assistance needs with modest premium increase."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baker. I have a travel insurance inquiry.
<agent>: Good afternoon Mr. Baker, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm planning a hiking trip in the Himalayas. Does my travel insurance cover high-altitude activities?
<agent>: That's an adventure! Let me check your policy RV-3399-H8... You have standard travel insurance which has altitude restrictions.
<customer>: What kind of restrictions?
<agent>: Standard coverage applies up to 4,500 meters altitude. Above that, you need specialized high-altitude coverage.
<customer>: The trek goes up to 5,500 meters. What are my options?
<agent>: We can arrange an extension for high-altitude activities, including helicopter evacuation if needed.
<customer>: Helicopter evacuation? That sounds expensive.
<agent>: It is, but essential at those altitudes where normal rescue isn't possible. The extension is about 200 francs for a two-week trip.
<customer>: That's reasonable for peace of mind. Please arrange the high-altitude coverage.""",
        "topics": ["11"],
        "summary": "Customer planning Himalayan trek needs high-altitude travel insurance extension above 4,500 meters. Coverage includes specialized evacuation services."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Schmid. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Frau Schmid, hier ist Pascal Tremblay. Wie kann ich helfen?
<customer>: Mein Mann ist verstorben und ich muss die Leistung beantragen.
<agent>: Mein herzliches Beileid, Frau Schmid. Ich helfe Ihnen gerne bei allen Formalitäten.
<customer>: Welche Unterlagen brauchen Sie?
<agent>: Den Sterbeausweis, eine Kopie des Ehescheins und ein ausgefülltes Leistungsformular.
<customer>: Wie lange dauert die Bearbeitung normalerweise?
<agent>: Nach Eingang aller Unterlagen etwa 10-14 Tage. In besonderen Härtefällen können wir eine Vorauszahlung leisten.
<customer>: Das wäre hilfreich, da ich hohe Bestattungskosten habe.
<agent>: Das verstehe ich. Ich sende Ihnen alle Formulare und organisiere eine Vorauszahlung von 50% der Versicherungssumme.
<customer>: Vielen Dank für Ihr Verständnis und Ihre Hilfe.
<agent>: Das ist selbstverständlich in dieser schweren Zeit.""",
        "topics": ["12"],
        "summary": "Widow applies for life insurance benefits after husband's death. Agent offers compassionate processing with 50% advance payment to help with funeral costs."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Taylor. I have a question about my valuables coverage.
<agent>: Hello Ms. Taylor, this is Sarah Dürst from Vaudoise. What would you like to know?
<customer>: I'm getting married and received expensive wedding gifts. How do I add them to my insurance?
<agent>: Congratulations on your wedding! New valuable items should be reported within 30 days of acquisition.
<customer>: What constitutes a valuable item that needs special coverage?
<agent>: Generally items worth more than 2,000 francs like jewelry, art, or collectibles should be individually listed.
<customer>: I received a diamond necklace and some silver pieces. Do I need appraisals?
<agent>: For items over 5,000 francs, we require professional appraisals. For others, purchase receipts or gift documentation suffice.
<customer>: The necklace is worth about 8,000 francs. Can you recommend an appraiser?
<agent>: Certainly, I'll send you a list of certified jewelry appraisers in your area along with the coverage update forms.""",
        "topics": ["13"],
        "summary": "Newlywed needs to add expensive wedding gifts to valuables coverage. Agent explains reporting requirements and appraisal needs for high-value items.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Wolf. Ich habe eine grundlegende Frage zu Versicherungen.
<agent>: Guten Tag Herr Wolf, hier ist Marc Ducret. Womit kann ich Ihnen helfen?
<customer>: Ich ziehe bald ins Ausland und frage mich, was mit meinen Schweizer Versicherungen passiert.
<agent>: Das hängt davon ab, ob es ein vorübergehender oder dauerhafter Umzug ist und wohin Sie gehen.
<customer>: Ich gehe für mindestens fünf Jahre nach Deutschland für einen Job.
<agent>: Bei einem längerfristigen Umzug nach Deutschland können die meisten Versicherungen nicht einfach fortgeführt werden.
<customer>: Auch nicht die Lebensversicherung?
<agent>: Lebensversicherungen können oft fortgeführt werden, aber Sachversicherungen wie Auto und Hausrat müssen normalerweise gekündigt werden.
<customer>: Was ist mit meinen Rabatten und der Schadenfreiheit?
<agent>: Die Schadenfreiheit können wir Ihnen bescheinigen für die Verwendung bei deutschen Versicherern.
<customer>: Das ist gut zu wissen. Können Sie mir eine komplette Übersicht machen?
<agent>: Sehr gerne. Ich erstelle Ihnen eine detaillierte Auswanderer-Checkliste für alle Ihre Policen.""",
        "topics": ["1"],
        "summary": "Customer moving to Germany for work asks about insurance implications. Agent explains different rules for life vs property insurance and offers emigration checklist."
    },
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
        "suggested_topics": ["1"],
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
        "suggested_topics": ["2"],
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
        "suggested_topics": ["2"],
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
    }, # DUPLICATING FOR EXTRA VOLUMES - Remove if necessary
{
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe eine allgemeine Frage zu meinen Versicherungen bei der Vaudoise.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Womit kann ich Ihnen helfen?
<customer>: Ich habe so viele verschiedene Policen, dass ich langsam den Überblick verliere. Können Sie mir sagen, was aktuell alles bei mir versichert ist?
<agent>: Natürlich. Dann starte ich am besten einen Gesamtüberblick. Haben Sie bitte kurz Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 45-AN-1295-M8.
<agent>: Vielen Dank. Einen Moment… ich sehe hier eine Hausrat-, eine Fahrzeug- und eine Reiseversicherung. Dazu noch eine kleine Lebensversicherung.
<customer>: Und wie sieht es mit einer Rechtsschutzversicherung aus? Ich dachte, ich hätte eine.
<agent>: Ich sehe im System keinen aktiven Rechtsschutzvertrag. Wir könnten prüfen, ob das für Sie sinnvoll wäre.
<customer>: Hm, das überrascht mich. Ich war sicher, dass ich eine habe. Das ärgert mich gerade ein bisschen.
<agent>: Das verstehe ich gut. Wenn Sie möchten, kann ich Ihnen eine kurze Zusammenstellung inkl. Offerte für eine Rechtsschutzversicherung per E-Mail schicken.
<customer>: Ja, tun Sie das bitte. Aber ich entscheide danach in Ruhe. Keine automatische Aktivierung!
<agent>: Selbstverständlich, es handelt sich nur um eine unverbindliche Offerte. Ist die E-Mail-Adresse dvorak@gmail.com noch aktuell?
<customer>: Ja, die stimmt.
<agent>: Perfekt, dann erhalten Sie im Laufe des Tages eine Übersicht über Ihre bestehenden Policen und einen separaten Vorschlag für die Rechtsschutzversicherung.
<customer>: Gut, danke. Dann warte ich darauf.
<agent>: Sehr gerne, Frau Dvorak. Wenn danach noch Fragen offen sind, können Sie uns jederzeit wieder anrufen.""",
        "topics": ["1"],
        "summary": "Customer wants a complete overview of her existing insurance policies and discovers that no legal protection insurance is present. She receives an overview and a non-binding quote.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe das Gefühl, dass ich bei der Vaudoise nicht alles versichert habe, was ich eigentlich brauche.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Welche Situation beschäftigt Sie konkret?
<customer>: Wir haben kürzlich eine kleine Ferienwohnung gekauft, und mir ist aufgefallen, dass diese nirgends explizit erwähnt ist.
<agent>: Verstehe. Dann schauen wir uns Ihre Policen an. Könnten Sie mir bitte Ihre Kundennummer oder eine Policennummer geben?
<customer>: Die Policennummer ist UD-5715-K7.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung aktuell nur auf Ihre Hauptwohnung läuft. Die Ferienwohnung ist tatsächlich nicht eingeschlossen.
<customer>: Das ist genau das, was ich befürchtet habe. Wenn dort etwas passiert, stehe ich dann komplett ohne Schutz da?
<agent>: Für Schäden vor Ort, ja, aktuell wäre dort keine Deckung. Wir können das Objekt aber relativ einfach in Ihre Hausratversicherung integrieren oder separat versichern.
<customer>: Warum hat mir das niemand gesagt, als ich angerufen habe, bevor wir gekauft haben?
<agent>: Es tut mir leid, wenn das damals nicht klar kommuniziert wurde. Ich kann Ihren Fall intern vermerken, damit wir das überprüfen.
<customer>: Ich bin ehrlich gesagt ziemlich verärgert. Das ist doch Ihr Job, mich auf solche Lücken hinzuweisen.
<agent>: Ich verstehe Ihren Ärger sehr gut. Als Sofortmassnahme könnte ich Ihnen eine provisorische Deckung ab heute einrichten, damit Sie nicht länger ohne Schutz sind. Die definitive Police würden wir Ihnen dann schriftlich zustellen.
<customer>: Gut, dann machen Sie das bitte. Aber ich möchte keine versteckten Zusatzkosten.
<agent>: Selbstverständlich. Ich sende Ihnen noch heute eine transparente Offerte mit allen Prämien und Leistungen. Erst wenn Sie unterschreiben, wird die Police definitiv.
<customer>: In Ordnung, dann warte ich auf die Unterlagen. Wenn mir etwas komisch vorkommt, melde ich mich wieder.
<agent>: Das ist absolut in Ordnung. Vielen Dank für Ihre Offenheit, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer discovers that her new holiday apartment is not insured, is annoyed, and receives provisional coverage as well as a transparent quote to close the coverage gap.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Simic. I'm interested in additional insurance with Vaudoise.
<agent>: Good afternoon Mr. Simic, this is Nora Widmer. Nice that you're contacting us. What did you have in mind?
<customer>: I bought a new electric car and I'm wondering if I need something special for it.
<agent>: Congratulations on the new car! Do you drive the vehicle mainly privately or also for business?
<customer>: Only privately, but quite a lot. And I heard that batteries are very expensive if something happens to them.
<agent>: That's correct. We have a special module for electric vehicles that covers battery damage and extends assistance services.
<customer>: Sounds interesting. Can you give me an approximate idea of what this would cost me per year?
<agent>: If I base this on your current vehicle insurance with policy number VK-8002-K3, the additional module would be around 120 francs per year.
<customer>: Hmm. I honestly expected less.
<agent>: I understand. We could check whether you want optimizations on the deductible or other coverage to keep the overall premium stable.
<customer>: No, I don't want to tinker around everywhere. Just send me an offer, then I'll decide.
<agent>: Gladly. To which email address may I send the quote? I still have simic@gmail.com.
<customer>: Yes, that's correct. But please without automatic salutation "Dear Family", I hate that.
<agent>: Alright, I'll note that. You'll receive a personal quote addressed only to you.
<customer>: Good, then let's wait and see what comes.
<agent>: Very gladly, Mr. Simic. If you have questions afterwards or want to conclude directly, just contact us.""",
        "topics": ["3"],
        "summary": "Customer is interested in expanding his vehicle insurance for a new electric car. He has a quote sent to him but doesn't want any adjustments to other coverage for now.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. Il s'agit de mon sinistre en cours chez Vaudoise, et je ne suis pas satisfaite.
<agent>: Bonjour Madame Roth, ici Anna Meier. Je regrette d'apprendre que vous n'êtes pas satisfaite. De quel sinistre s'agit-il?
<customer>: Il s'agit des dégâts d'eau dans mon appartement, numéro de référence SV-5385-I9. Vous ne voulez me rembourser qu'une partie des coûts.
<agent>: Un moment, j'ouvre le dossier... Oui, je vois qu'une partie des coûts a été classée comme entretien non assuré.
<customer>: C'est exactement ce que je trouve injuste. J'ai tout fait entretenir régulièrement. Maintenant je me retrouve avec plusieurs milliers de francs à ma charge.
<agent>: Je comprends que ce soit frustrant. Selon l'expertise, les conduites étaient déjà fortement corrodées, ce qui constitue un défaut préexistant.
<customer>: Je ne peux pas accepter cela ainsi. Je n'ai jamais reçu d'écrit disant que quelque chose n'était pas en ordre.
<agent>: Ce que je peux faire pour vous: nous pouvons faire procéder à une seconde évaluation par un expert indépendant. Cela peut cependant prendre quelques jours.
<customer>: Franchement, j'en ai assez de ces "quelques jours". Cela traîne depuis des semaines.
<agent>: Je peux le comprendre. Alternativement, nous pourrions examiner un montant partiel comme paiement de complaisance, sans reconnaissance d'obligation légale.
<customer>: Alors, soit vous prenez en charge davantage, soit je vais voir l'ombudsman.
<agent>: Bien sûr, la voie vers l'ombudsman vous est ouverte. Je vous propose que j'escalade le dossier dès aujourd'hui à notre direction sinistres et que nous vous fassions parvenir une prise de position concrète au plus tard après-demain.
<customer>: Bien, faites cela. Mais si je reçois encore une réponse standard, vous ne me reverrez sûrement plus comme cliente.
<agent>: Je prends votre feedback très au sérieux et note votre plainte en détail dans le dossier.
<customer>: D'accord, alors j'attends maintenant UNE dernière fois votre retour.
<agent>: Merci pour votre patience, Madame Roth. Nous vous recontacterons le plus rapidement possible.""",
        "topics": ["4"],
        "summary": "Customer is dissatisfied with compensation after water damage. The case is escalated to claims management, a new review or possible goodwill solution is announced."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Steiner. Ich rufe wegen meines offenen Schadenfalls an. Ich habe seit zwei Wochen nichts mehr gehört.
<agent>: Guten Tag Frau Steiner, hier ist Sarah Dürst von der Vaudoise. Darf ich bitte die Schadenreferenz haben?
<customer>: Ja, das ist SN-2993-Z3.
<agent>: Vielen Dank. Ich schaue kurz nach… Ich sehe, dass wir noch auf eine Rückmeldung der Werkstatt warten, die die Reparaturkosten bestätigen soll.
<customer>: Das kann doch nicht Ihr Ernst sein. Ich habe das Auto vor zehn Tagen zurückbekommen.
<agent>: Es tut mir leid, dass das so lange dauert. Im System ist noch keine finale Rechnung hinterlegt.
<customer>: Ich habe die Rechnung gestern selber per E-Mail geschickt!
<agent>: Einen Moment… ah, ich sehe sie jetzt in unserem Posteingang, aber sie ist noch nicht im Dossier verbucht. Das hätte schneller passieren sollen, da gebe ich Ihnen recht.
<customer>: Ja, genau. Ich kann nicht ständig hinterhertelefonieren.
<agent>: Ich priorisiere Ihren Fall sofort und gebe ihn an die zuständige Schadensachbearbeiterin weiter. Sie erhalten spätestens morgen eine Bestätigung der Auszahlung.
<customer>: Versprechen Sie mir das? Ich habe schon einmal „morgen" gehört.
<agent>: Ich kann Ihnen zusagen, dass ich persönlich einen Reminder setze und Sie morgen Vormittag per E-Mail über den Status informiere.
<customer>: Gut. Wenn ich morgen nichts höre, rufe ich direkt Ihre Vorgesetzte an.
<agent>: Das verstehe ich. Ich kümmere mich darum, dass es gar nicht so weit kommt.
<customer>: Na gut, dann warte ich bis morgen.
<agent>: Vielen Dank, Frau Steiner. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for settlement of a claim. The agent finds an unposted invoice and prioritizes the case, including a personal status update the next day."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller speaking. I have a question about my premiums and payments.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What exactly is it about?
<customer>: I received a reminder yesterday, even though I'm sure I paid.
<agent>: Let's clarify this. Do you have the policy number at hand?
<customer>: Yes, PZ-2519-D4.
<agent>: Thanks. One moment... I see that the premium for the second quarter is still outstanding. Do you perhaps have a payment receipt or the date of the transfer?
<customer>: I paid in the middle of the month. Honestly, this is getting annoying, it's not the first time this happens.
<agent>: I understand that. If you want, you can send me the payment receipt by email, then we'll reconcile the payment with our bookings.
<customer>: Do I have to do this again? Can't you just check the bank?
<agent>: For data protection reasons, we only see our account movements. Without a receipt, it's difficult to search for a specific transfer. However, I can commission an internal reconciliation in parallel.
<customer>: Good, I'll forward you the screenshot from e-banking to keller@gmail.com. Are you using this address?
<agent>: Yes, exactly this one is registered. I'll note that the reminder fee is suspended for now until we've clarified the case.
<customer>: At least that. I definitely don't want to appear as a defaulting payer.
<agent>: That's understandable. As soon as we've found the payment receipt, you'll receive a confirmation and the reminder will be deleted.
<customer>: Okay, then I'll do that right after the phone call.
<agent>: Thank you very much, Mr. Keller. We'll take care of it.""",
        "topics": ["6"],
        "summary": "Customer receives a reminder despite having made payment. The agent suspends the reminder fee and requests payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Alonso. Ich habe einige Fragen zu den Leistungen meiner Gesundheitsunterstützung bei der Vaudoise.
<agent>: Guten Tag Frau Alonso, hier ist Anna Meier. Erzählen Sie mir, worum es konkret geht.
<customer>: Mein Arzt hat mir eine Psychotherapie empfohlen. Ich weiss aber nicht, was genau und wie lange die Vaudoise beteiligt ist.
<agent>: Dafür schauen wir am besten in Ihre Police. Haben Sie Ihre Policennummer zur Hand?
<customer>: Ja, GS-6059-J5.
<agent>: Danke, ich habe Ihre Unterlagen vor mir. Sie haben ein Zusatzpaket mit Beteiligung an ambulanten Therapien.
<customer>: Bedeutet das, dass alles übernommen wird?
<agent>: Nicht ganz. Ich erkläre es Ihnen Schritt für Schritt:
<agent>: Erstens: Es gibt einen Selbstbehalt von 10% auf die Kosten, nachdem die Franchise der Grundversicherung erreicht ist.
<customer>: Okay, und zweitens?
<agent>: Zweitens: Es ist eine maximale Anzahl von 40 Sitzungen pro Jahr vorgesehen, sofern die Therapie ärztlich verordnet und von einer anerkannten Fachperson durchgeführt wird.
<customer>: Und wenn ich mehr als 40 Sitzungen brauche?
<agent>: Drittens: Darüber hinaus gehende Sitzungen können auf Antrag geprüft werden, es gibt aber keine Garantie, dass sie übernommen werden.
<customer>: Verstehe. Viertens?
<agent>: Viertens: Für die erste Kostengutsprache benötigen wir einen Bericht Ihrer behandelnden Ärztin oder Ihres Arztes.
<customer>: Das heisst, ich muss zuerst zum Hausarzt?
<agent>: Genau, fünftens: Der Antrag muss über Ihre Hausärztin oder Ihren Hausarzt laufen. Sie oder er reicht die Unterlagen direkt bei uns ein.
<customer>: Puh, das ist komplizierter als gedacht, aber jetzt habe ich es verstanden.
<agent>: Gerne fasse ich Ihnen alles in einer E-Mail zusammen, damit Sie es in Ruhe nachlesen können. Ist alonso@hotmail.com noch aktuell?
<customer>: Ja, das passt.
<agent>: Wunderbar, dann sende ich Ihnen die Zusammenfassung und ein Merkblatt noch heute.
<customer>: Danke, das hilft mir sehr.
<agent>: Dafür sind wir da, Frau Alonso.""",
        "topics": ["7"],
        "summary": "Customer inquires about coverage for psychotherapy. The agent explains deductible, session count, and application process and sends a written summary."
    },
    {
        "transcript": """<customer>: Hallo, hier ist Herr Keller. Mein Auto ist eben liegengeblieben und ich brauche dringend Pannenhilfe.
<agent>: Guten Tag Herr Keller, hier ist Luca Steiner von der Vaudoise Assistance. Sind Sie und alle Mitfahrenden in Sicherheit?
<customer>: Ja, wir stehen auf einem Parkplatz, aber das Auto springt nicht mehr an.
<agent>: Gut, dann beruhigt mich das schon einmal. Wo genau befinden Sie sich?
<customer>: Auf der A2 Raststätte Richtung Luzern, kurz nach der Ausfahrt Sursee.
<agent>: Danke. Haben Sie Ihre Policennummer oder Ihr Kennzeichen zur Hand?
<customer>: Kennzeichen ist LU 123 456, Policennummer müsste PH-2385-L9 sein.
<agent>: Perfekt, ich sehe, Sie haben das erweiterte Pannenhilfe-Paket. Ich kann sofort einen Abschleppdienst organisieren.
<customer>: Wie lange dauert das ungefähr?
<agent>: Erfahrungsgemäss 30 bis 45 Minuten, je nach Verkehrslage. Der Pannendienst bringt Ihr Fahrzeug zu einer Partnergarage oder auf Wunsch zu Ihrer Stammgarage.
<customer>: In Ordnung. Und was kostet mich das?
<agent>: Der Einsatz selbst ist durch Ihre Pannenhilfe gedeckt. Allfällige Reparaturkosten in der Garage gehen separat.
<customer>: Gut, dann schicken Sie jemanden. Meine Handynummer ist dieselbe wie im System.
<agent>: Ich habe sie hier, der Pannendienst wird Sie kurz vor Ankunft direkt anrufen.
<customer>: Alles klar, danke.
<agent>: Gern geschehen, Herr Keller. Bleiben Sie unbedingt hinter der Leitplanke, falls Sie doch nahe der Autobahn stehen.""",
        "topics": ["8"],
        "summary": "Customer needs immediate roadside assistance on the highway. Assistance organizes a towing service that is covered by the roadside assistance package."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have a question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Marc Ducret from Vaudoise. What's the matter?
<customer>: We bought some new, quite expensive furniture. I'm not sure if the insurance sum is still sufficient.
<agent>: Then let's check that together. Do you have your policy number at hand?
<customer>: Yes, HR-8435-W3.
<agent>: Thanks. Your current insurance sum is 60,000 francs. Do you have an approximate idea of the total value of your household contents after the new purchase?
<customer>: Hard to say, but I think it's rather around 80,000 francs.
<agent>: Then there is indeed a risk of underinsurance. In case of damage, this would mean that compensations could be reduced.
<customer>: I definitely don't want that. But I also don't want to pay unnecessarily high premiums.
<agent>: Understandable. We could offer a free household contents check where you record a list of your largest items online. This results in a realistic insurance sum.
<customer>: Does someone have to come by?
<agent>: No, you can do that conveniently yourself. If you want, I can send you the link to the tool by email and then adjust the policy accordingly.
<customer>: Alright, let's do it that way.
<agent>: Perfect. I'll send you the link to steiner@gmail.com and a proposal for the new insurance sum.
<customer>: Good, then I'll look at that tonight.
<agent>: Thank you very much, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer has significantly upgraded her household contents and fears underinsurance. She receives an online tool to determine an appropriate insurance sum."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich habe Fragen zu meiner Fahrzeugversicherung bei der Vaudoise.
<agent>: Guten Tag Herr Simic, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich hatte einen Steinschlag in der Frontscheibe, und die Werkstatt meint, ich soll das über die Versicherung laufen lassen. Verliere ich dann meinen Bonus?
<agent>: Schauen wir zuerst in Ihre Police. Haben Sie die Nummer zur Hand?
<customer>: Ja, FV-1234-P3.
<agent>: Danke. Sie haben eine Vollkaskoversicherung mit einem speziellen Bonus-Schutz-Modul.
<customer>: Und was heisst das konkret?
<agent>: Das bedeutet, dass ein einzelner Glasschaden Ihren Bonus nicht reduziert. Sie zahlen nur die vereinbarte Selbstbeteiligung, falls überhaupt eine vorgesehen ist.
<customer>: Das klingt schon mal besser. Wie hoch ist die Selbstbeteiligung?
<agent>: Bei Glasschäden ist bei Ihnen keine Selbstbeteiligung hinterlegt.
<customer>: Also zahle ich gar nichts?
<agent>: Die Reparatur der Scheibe wäre in Ihrem Fall vollständig gedeckt, sofern sie bei einer anerkannten Partnerwerkstatt erfolgt.
<customer>: Okay, das ist fair. Können Sie mir eine Liste der Partnerwerkstätten in meiner Nähe per E-Mail senden?
<agent>: Sehr gerne. Ich sende Ihnen eine Übersicht für den Raum Luzern an simic@gmail.com.
<customer>: Super, dann bin ich zufrieden.
<agent>: Freut mich, dass ich helfen konnte, Herr Simic.""",
        "topics": ["10"],
        "summary": "Customer inquires whether glass damage affects his bonus. Thanks to bonus protection and no deductible, the repair is fully covered."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. J'ai une question sur mon assurance voyage.
<agent>: Bonjour Monsieur Berger, ici Marc Ducret de Vaudoise. De quoi s'agit-il?
<customer>: Je pars la semaine prochaine en Thaïlande. Comment cela se passe-t-il si je ne peux pas voyager à cause d'une maladie soudaine?
<agent>: Pour cela, je regarde rapidement dans votre police RV-1208-B3. Vous avez souscrit une assurance frais d'annulation.
<customer>: Et qu'est-ce que cela couvre exactement?
<agent>: Si vous ou une personne co-assurée tombez gravement malades ou avez un accident avant le voyage, nous prenons en charge les frais d'annulation contractuellement dus selon les conditions.
<customer>: Avez-vous alors besoin d'un certificat médical?
<agent>: Oui, une attestation médicale est requise, dont il ressort que le voyage ne peut pas être entrepris d'un point de vue médical.
<customer>: Et si un avertissement de voyage officiel est prononcé?
<agent>: Selon la situation, la couverture est examinée par le biais d'une autre clause, par exemple en cas de force majeure. Nous nous orientons également selon les conseils de voyage de la Confédération.
<customer>: Bien, au moins je ne suis pas complètement livré à moi-même.
<agent>: Exactement, vous avez une protection solide. Si vous voulez, je vous envoie un court mémo sur les points les plus importants.
<customer>: Oui, s'il vous plaît à berger@gmail.com.
<agent>: Je le fais volontiers, Monsieur Berger.""",
        "topics": ["11"],
        "summary": "Customer inquires about cancellation protection in case of illness and travel warnings. The agent explains coverage and requirements, including medical certificate."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Alonso. I have questions about my life insurance with Vaudoise.
<agent>: Good afternoon Mrs. Alonso, this is Sarah Dürst. What would you like to know?
<customer>: My life situation has changed, I now have a child. I'm wondering if the insurance sum is still sensible.
<agent>: Then it's a good time to look at that. Do you have your policy number ready?
<customer>: Yes, LV-4995-Q2.
<agent>: Thanks. Your current insurance sum is 100,000 francs. Do you have an idea of what you'd like as a target sum?
<customer>: Rather 200,000 francs, so that in the worst case at least the mortgage is partially covered.
<agent>: I understand. An increase is basically possible, but a renewed health examination may be required.
<customer>: What exactly does that mean?
<agent>: You would fill out a health questionnaire, and depending on the sum and age, a medical examination could be added.
<customer>: And if something is found?
<agent>: Then there can be reservations or a surcharge. I recommend that we first create a non-binding quote with different variants.
<customer>: Alright. Please send me two variants: one with 150,000 and one with 200,000.
<agent>: Very gladly. I'll send you the quotes to alonso@gmail.com.
<customer>: Thanks, then I'll discuss this with my partner.
<agent>: That's a good idea, Mrs. Alonso.""",
        "topics": ["12"],
        "summary": "Customer has had offspring and wants to increase the insurance sum of her life insurance. A quote with two variants and reference to possible health examination is created."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Wertsachenversicherung.
<agent>: Guten Tag Herr Keller, hier ist Anna Meier von der Vaudoise. Was liegt an?
<customer>: Ich habe eine neue Uhr gekauft, die nicht ganz billig war. Ich möchte wissen, ob die automatisch mitversichert ist.
<agent>: Haben Sie die Policennummer Ihrer Wertsachenversicherung?
<customer>: Ja, WV-6297-D2.
<agent>: Danke. Sie haben eine Pauschaldeckung für Wertsachen bis 20'000 Franken. Wissen Sie ungefähr, wo Sie aktuell mit dem Gesamtwert liegen?
<customer>: Mit der neuen Uhr komme ich wahrscheinlich knapp über 20'000 Franken.
<agent>: Dann wäre es sinnvoll, die Uhr entweder einzeln zu deklarieren oder die Pauschalsumme zu erhöhen.
<customer>: Und was empfehlen Sie?
<agent>: Wenn es sich um ein besonders wertvolles Einzelstück handelt, ist eine Einzeldeklaration vorteilhaft – unter anderem im Schadenfall.
<customer>: In Ordnung. Ich lasse Ihnen die Rechnung und ein Foto zukommen.
<agent>: Perfekt. Senden Sie die Unterlagen bitte an unsere E-Mail-Adresse, die ich Ihnen gleich per Mail zur Bestätigung schicke.
<customer>: Passt, danke.
<agent>: Sehr gerne, Herr Keller.""",
        "topics": ["13"],
        "summary": "Customer wants to insure a new, expensive watch. The agent recommends individual declaration or increasing the lump sum and requests documents."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about my insurance.
<agent>: Good afternoon Mr. Baumann, this is Pascal Tremblay from Vaudoise. What concerns you?
<customer>: I feel like I have too many individual policies and everything is too complicated.
<agent>: I hear that often. We can check a so-called policy bundling.
<customer>: What does that bring me?
<agent>: First: You have fewer documents and a better overview. Second: Often there's a bundling discount. Third: Adjustments can be made more easily.
<customer>: Sounds logical. But I don't want to suddenly be worse insured.
<agent>: I understand that. We would compare your existing coverage point by point:
<agent>: 1. Which risks are covered today?
<agent>: 2. Which coverage could be merged?
<agent>: 3. Where are there duplicate insurances?
<customer>: Duplicate insurances? That would be wasted money.
<agent>: Exactly, and fourth we would check whether the insurance sums still fit your current life situation.
<customer>: And how does that work concretely?
<agent>: I'll send you an overview of your policies in advance by email to baumann@hotmail.com. After that we can arrange a consultation appointment, by phone or on-site.
<customer>: A phone appointment is enough for me first.
<agent>: Good, I'll send you two appointment suggestions for next week right away.
<customer>: Alright, then I'll decide on one of them.
<agent>: Perfect, Mr. Baumann.""",
        "topics": ["1"],
        "summary": "Customer feels overwhelmed by the number of his policies. A bundling with possible discount and structured review of coverage is proposed.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich habe das Gefühl, dass ich bei Ihnen nicht ausreichend versichert bin.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Was lässt Sie das vermuten?
<customer>: Eine Freundin hatte einen Brand im Keller, und ein Teil war nicht gedeckt. Jetzt frage ich mich, ob ich auch so eine Lücke habe.
<agent>: Dann prüfen wir das besser. Haben Sie Ihre Policennummer oder Kundennummer zur Hand?
<customer>: UD-3205-U3.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung eine relativ tiefe Versicherungssumme ausweist und keine speziellen Zusatzdeckungen für Fahrräder oder Schmuck besitzt.
<customer>: Super. Und das haben Sie mir nicht mal aktiv gesagt.
<agent>: Es tut mir leid, wenn das bisher nicht ausführlich besprochen wurde. Wir können jetzt gemeinsam schauen, was Ihnen wichtig ist.
<customer>: Wichtig ist mir, dass ich im Ernstfall nicht pleite bin.
<agent>: Verstehe. Wir könnten:
<agent>: – die Versicherungssumme erhöhen,
<agent>: – eine spezielle Wertsachendeckung hinzufügen,
<agent>: – und prüfen, ob gewisse Risiken wie Elementarschäden besser abgedeckt werden sollten.
<customer>: Klingt nach höheren Kosten.
<agent>: Es würde die Prämie leicht erhöhen, aber ich kann Ihnen zwei Varianten erstellen: eine Minimalanpassung und eine umfassendere Lösung.
<customer>: Schicken Sie mir beides. Aber ehrlich: Wenn ich das Gefühl habe, dass Sie einfach nur verkaufen wollen, wechsle ich die Versicherung.
<agent>: Ich verstehe Ihre Sorge. Ich werde alles transparent aufschlüsseln, damit Sie selbst entscheiden können.
<customer>: Gut, dann schaue ich mir das an.
<agent>: Vielen Dank, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer suspects gaps in her household contents and valuables coverage. Various adjustment variants with different premium levels are announced.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une demande de vente.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer de Vaudoise. De quoi s'agit-il?
<customer>: Je déménage dans un nouvel appartement, et mon propriétaire exige une assurance responsabilité civile privée et ménage. Mais j'ai actuellement seulement l'assurance auto et voyage.
<agent>: Alors regardons comment nous pouvons compléter cela. Voulez-vous souscrire les deux - ménage et responsabilité civile privée - ensemble?
<customer>: Oui, mais cela ne doit pas être trop cher.
<agent>: Si nous définissons cela comme un paquet, nous pouvons offrir un rabais de combinaison.
<customer>: Pouvez-vous me donner une valeur indicative maintenant?
<agent>: Basé sur votre profil - lieu de résidence, âge et contrats déjà existants - j'estime environ 280 à 320 francs par an pour les deux ensemble.
<customer>: Cela va. Mais j'ai besoin de cela assez urgemment, sinon il y aura des problèmes avec le propriétaire.
<agent>: Nous pourrions créer aujourd'hui une attestation de couverture provisoire. Les documents définitifs, vous les recevrez ensuite par courrier ou email.
<customer>: D'accord. Alors faisons cela.
<agent>: Parfait. Je vous envoie d'abord un bref résumé par email à keller@gmail.com. Dès que vous confirmez, je génère l'attestation de couverture pour votre propriétaire.
<customer>: Faites vite s'il vous plaît, je dois lui donner cela au plus tard demain.
<agent>: Je m'en occupe tout de suite après, Monsieur Keller.""",
        "topics": ["3"],
        "summary": "Customer urgently needs household contents and personal liability insurance for a new apartment. A package with combination discount and provisional coverage certificate is offered."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverhandlung an, und ehrlich gesagt bin ich ziemlich sauer.
<agent>: Guten Tag Frau Dvorak, hier ist Marc Ducret. Es tut mir leid, dass Sie verärgert sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruch bei mir zuhause, Referenz SV-3253-C3. Sie haben diverse Positionen einfach gestrichen.
<agent>: Ich öffne den Fall… Einen Moment bitte… Ja, ich sehe die Korrespondenz. Einige Gegenstände konnten nicht belegt werden.
<customer>: Natürlich habe ich keine Rechnung von einer fünf Jahre alten Tasche mehr. Deswegen war sie ja trotzdem da!
<agent>: Ich verstehe Ihre Sicht. Gemäss Bedingungen sind wir aber auf Nachweise angewiesen, damit wir den Wert einschätzen können.
<customer>: Also glauben Sie mir einfach nicht? Super.
<agent>: Darum geht es nicht. Wir brauchen Anhaltspunkte, zum Beispiel Fotos, Kontoauszüge oder Garantiekarten.
<customer>: Das habe ich schon alles geschickt. Lesen Sie Ihre Mails?
<agent>: Ich sehe, dass gestern tatsächlich noch Fotos nachgereicht wurden, die aber noch nicht im System verknüpft sind. Das hätte schneller gehen müssen, entschuldigen Sie bitte.
<customer>: Ich habe langsam das Gefühl, ich werde hingehalten, damit ich aufgebe.
<agent>: Das ist ganz sicher nicht die Absicht. Ich werde den Fall noch heute an die zuständige Fachperson weitergeben und um eine erneute Prüfung der abgelehnten Positionen bitten.
<customer>: Gut. Wenn sich nichts bewegt, gehe ich damit zur Presse. Das meine ich ernst.
<agent>: Ich nehme Ihre Beschwerde sehr ernst und vermerke sie entsprechend. Sie erhalten bis spätestens Anfang nächster Woche eine schriftliche Stellungnahme.
<customer>: Wir werden sehen.
<agent>: Danke, dass Sie uns trotzdem noch einmal die Chance geben, das zu klären.""",
        "topics": ["4"],
        "summary": "Customer is annoyed about the rejection of burglary claim positions. After submitted photos, a new review is promised and the complaint is noted in the file."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Keller. I'm calling again about my open claim.
<agent>: Good afternoon Mr. Keller, this is Sarah Dürst from Vaudoise. Which claim is it about?
<customer>: Claim No. SN-5073-J8. I was told I would receive a payout last week. So far nothing is there.
<agent>: Let me check... It seems that the payment was released internally, but the bank connection was incomplete.
<customer>: You've had that from me a thousand times already!
<agent>: I see that the IBAN in the system is registered with two digits too few. That's naturally annoying, I'm sorry.
<customer>: That's more than annoying. I'm waiting for the money.
<agent>: Please give me your complete IBAN again so we can correct this.
<customer>: CH12 3456 7890 1234 5678 9.
<agent>: Thanks. I'll correct this immediately and forward the payment for processing again. Additionally, I'll note that any default interest should be checked.
<customer>: At least something. But quite honestly, the trust is pretty much gone by now.
<agent>: I can understand that. I can offer to send you a written confirmation about the renewed triggering this afternoon.
<customer>: Yes, I expect that too.
<agent>: Alright, Mr. Keller. Again, sorry for the circumstances.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for claim payment. Due to incorrect IBAN the payout was delayed, which is now corrected and triggered again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe schon wieder ein Schreiben zu offenen Prämien bekommen.
<agent>: Guten Tag Frau Roth, hier ist Yann Morel von der Vaudoise. Dann schauen wir uns das an. Haben Sie eine Referenznummer?
<customer>: Auf dem Brief steht PZ-6667-O4.
<agent>: Danke. Ich sehe, dass es sich um eine Prämienerhöhung aufgrund einer Vertragsverlängerung handelt. Vielleicht wirkt das wie ein neuer offener Betrag.
<customer>: Aber es ist deutlich mehr als letztes Jahr. Das kann doch nicht sein.
<agent>: Die Prämie wurde aufgrund höherer Schadenbelastung in Ihrem Segment angepasst. Zusätzlich ist eine Indexierung eingeflossen.
<customer>: Das heisst auf gut Deutsch: Ich zahle mehr, ohne dass ich etwas dafür bekomme.
<agent>: Die Deckung bleibt zwar gleich, aber die Kosten im Hintergrund steigen. Auf Wunsch könnten wir Deckungen anpassen, um die Prämie zu reduzieren.
<customer>: Zum Beispiel?
<agent>: Man könnte die Selbstbeteiligung leicht erhöhen oder einzelne optionale Zusatzbausteine streichen.
<customer>: Und wenn ich das nicht will?
<agent>: Dann bleibt die Prämie wie im Schreiben angegeben. Selbstverständlich steht es Ihnen frei, den Markt zu vergleichen.
<customer>: Vielleicht mache ich das. Im Moment bin ich wirklich nicht begeistert.
<agent>: Das verstehe ich. Wenn Sie möchten, kann ich Ihnen mindestens ein oder zwei Sparvarianten ausrechnen und per E-Mail senden.
<customer>: Schicken Sie es an roth@gmail.com. Aber ohne Schönrederei.
<agent>: Ich sende Ihnen eine nüchterne Aufstellung, versprochen.""",
        "topics": ["6"],
        "summary": "Customer is annoyed about a significant premium increase. The agent explains reasons and offers savings variants through coverage adjustment."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. J'ai des questions de santé en relation avec ma police.
<agent>: Bonjour Madame Roth, ici Pascal Tremblay. En quoi puis-je vous aider?
<customer>: J'ai été inscrite pour une réhabilitation, et la clinique veut savoir ce que Vaudoise prend exactement en charge.
<agent>: Alors regardons dans votre police GS-1199-B4. Vous avez un paquet de réha avec une durée limitée.
<customer>: Combien de temps exactement?
<agent>: En principe, 21 jours de réha stationnaire par an sont couverts, pour autant qu'elle soit médicalement indiquée et approuvée au préalable.
<customer>: Mon médecin a dit que j'ai besoin d'au moins quatre semaines.
<agent>: Les jours supplémentaires pourraient passer par l'assurance de base ou un examen de cas individuel. Nous avons besoin pour cela d'un rapport détaillé de votre médecin.
<customer>: Et si cela est refusé?
<agent>: Alors les coûts supplémentaires seraient en partie ou entièrement à votre charge. Je recommande que nous demandions d'abord l'autorisation de coûts pour les 21 jours et examinions la prolongation en parallèle.
<customer>: D'accord, envoyez-moi une liste de ce que mon médecin doit soumettre.
<agent>: Très volontiers, je vous envoie un mémo à roth@gmail.com.
<customer>: Merci. J'espère que cela fonctionne sans paperasserie interminable.
<agent>: Nous essayons de garder le processus aussi simple que possible.""",
        "topics": ["7"],
        "summary": "Customer needs clarity about rehabilitation benefits. 21 days of rehabilitation are covered, an extension will be reviewed based on medical report."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich rufe wegen meiner Pannenhilfe an – beziehungsweise wegen deren Grenzen.
<agent>: Guten Tag Frau Roth, hier ist Nora Widmer von der Vaudoise. Was ist passiert?
<customer>: Gestern Nacht ist mein Auto in Deutschland stehen geblieben, und mir wurde gesagt, das sei nicht gedeckt.
<agent>: Ich schaue in Ihre Police PH-5104-L8… Sie haben eine Pannenhilfe, die standardmässig auf die Schweiz und das Fürstentum Liechtenstein beschränkt ist.
<customer>: Ja, das hat mir der Herr am Telefon dann auch gesagt – aber ganz ehrlich, das hätte man mir früher sagen müssen.
<agent>: Ich verstehe Ihren Ärger. Für Fahrten ins Ausland empfehlen wir ein erweitertes Assistance-Paket.
<customer>: Ja, jetzt weiss ich das auch. Bringt mir nur nichts mehr, das Taxi und der Rücktransport haben mich ein Vermögen gekostet.
<agent>: Für diesen konkreten Fall können wir leider nichts mehr rückwirkend decken. Was ich tun kann, ist Ihnen ein Angebot für die Zukunft zu machen.
<customer>: Das ist wenig tröstlich. Ich überlege mir ernsthaft, die Versicherung zu wechseln.
<agent>: Das tut mir sehr leid zu hören. Ich würde dennoch gerne sicherstellen, dass Sie künftig besser geschützt sind – ob bei uns oder anderswo. Darf ich Ihnen eine Übersicht über die möglichen Ausland-Assistance-Varianten schicken?
<customer>: Meinetwegen. Aber ehrlich, ich bin enttäuscht.
<agent>: Das kann ich nachvollziehen. Ich sende Ihnen die Übersicht an roth@gmail.com.
<customer>: Tun Sie das. Ich entscheide dann, ob ich bleibe.
<agent>: Danke, dass Sie uns trotzdem noch eine Chance geben, Frau Roth.""",
        "topics": ["8"],
        "summary": "Customer had a breakdown abroad that wasn't covered and is disappointed. The agent explains coverage limits and offers future foreign assistance options."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have another question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner from Vaudoise. What can I do for you?
<customer>: After the last phone call, I looked at your documents and found that my basement isn't specifically mentioned.
<agent>: Basement compartments are usually co-insured as long as they're at the same location. Let me quickly check your policy HR-1056-J5.
<customer>: But my basement is in the neighboring house. Does that count too?
<agent>: That's an important difference. If it's in another building, it might need a special agreement.
<customer>: And why doesn't anyone tell me this when I take out the policy?
<agent>: That could have been communicated more clearly, you're right there. But we can catch up on this now and explicitly include your basement in the policy.
<customer>: What does that cost me?
<agent>: That depends on the value of the stored items. If you give me a rough estimate, I can create a quote.
<customer>: Let's say 8,000 francs.
<agent>: Alright. I'll create a quote for you and send it to steiner@gmail.com. Only when you agree in writing will the coverage be extended.
<customer>: Good. This time I'll read everything very carefully.
<agent>: That's very sensible, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer discovers that her external basement compartment isn't clearly mentioned. A special agreement with quote for co-insurance is proposed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Es geht um meine Fahrzeugversicherung.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Worum geht es genau?
<customer>: Ich habe einen Brief bekommen, dass meine Kaskoversicherung wegen ausstehender Zahlung gesperrt wurde. Ich bin aber sicher, dass ich bezahlt habe.
<agent>: Lassen Sie mich Ihre Police FV-5163-G4 öffnen. Ich sehe hier tatsächlich eine temporäre Sistierung.
<customer>: Was heisst das konkret? Wenn ich jetzt einen Unfall habe, bin ich nicht versichert?
<agent>: Die Haftpflichtdeckung bleibt bestehen, aber Kaskoschäden wären momentan nicht gedeckt.
<customer>: Das ist ja wohl ein Witz. Ich habe vor zwei Wochen überwiesen.
<agent>: Es tut mir sehr leid. Wenn Sie möchten, können wir zusammen nachsehen, ob wir die Zahlung bereits erhalten haben und sie nur noch nicht zugeordnet wurde.
<customer>: Ich habe gerade keinen Beleg zur Hand, aber ich kann Ihnen später einen Screenshot schicken.
<agent>: Das wäre hilfreich. Alternativ könnten Sie den Betrag heute nochmals überweisen und wir würden bei Doppelzahlung umgehend zurückerstatten.
<customer>: Sicher nicht. Ich zahle nicht doppelt.
<agent>: Das verstehe ich. Dann warten wir auf Ihren Screenshot, setzen die Sistierung aber schon heute zur Überprüfung auf Priorität.
<customer>: Machen Sie das. Und bitte informieren Sie mich schriftlich, sobald alles wieder aktiv ist.
<agent>: Selbstverständlich, Frau Dvorak.""",
        "topics": ["10"],
        "summary": "Customer is annoyed about suspension of comprehensive coverage due to allegedly outstanding premium. She doesn't want to pay double amount and sends payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Baumann. I have a question about my travel insurance.
<agent>: Hello Mr. Baumann, this is Anna Meier from Vaudoise. What's it about?
<customer>: My flight was cancelled by the airline, and I was told I need to handle this through my insurance.
<agent>: Let me check your policy RV-7970-V7. Basically, in case of flight cancellations, the airline is primarily responsible.
<customer>: Yes, but they're currently pushing it to "force majeure" and only want to give me a voucher.
<agent>: In such cases, your travel insurance can partially help, for example with additional costs for hotel or replacement flight, depending on the cause.
<customer>: It was a strike. Does that count?
<agent>: Strikes are covered to a limited extent in many policies. I see that your contract provides certain benefits, but only under certain conditions.
<customer>: Quite honestly, I feel like I'm being pushed around between airline and insurance.
<agent>: I can understand that well. What I can do: Send us the written statement from the airline, and we'll check specifically which positions we can cover.
<customer>: Good, then I'll do that. But I expect a clear answer, not just paragraphs.
<agent>: I'll explicitly note this hint in the file so that the answer is formulated as understandably as possible.""",
        "topics": ["11"],
        "summary": "Customer is caught between airline and insurance after flight cancellation. The agent requests documents to check travel insurance coverage for strikes."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer von der Vaudoise. Wie kann ich helfen?
<customer>: Ich überlege mir, die Police ganz zu kündigen. Ich zahle schon so viel und habe das Gefühl, ich brauche das nicht.
<agent>: Dann sollten wir gemeinsam anschauen, was die Konsequenzen wären. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-5949-B6.
<agent>: Danke. Bei einer Kündigung jetzt würden Sie einen Rückkaufswert erhalten, der unter der bisher einbezahlten Summe liegt.
<customer>: Das klingt nicht gerade attraktiv.
<agent>: Nein, kurzfristig ist der Rückkaufswert oft tiefer. Langfristig bietet die Police einen Todesfallschutz und teilweise auch Sparkomponenten.
<customer>: Ich weiss, aber das Geld fehlt mir im Alltag.
<agent>: Eine Alternative wäre, die Prämie zu reduzieren oder den Vertrag für eine gewisse Zeit prämienfrei zu stellen, anstatt ihn ganz zu beenden.
<customer>: Heisst das, ich würde vorübergehend nichts mehr zahlen?
<agent>: Genau. Die Leistungen würden entsprechend reduziert, aber der Vertrag bliebe bestehen.
<customer>: Schicken Sie mir bitte beide Varianten: Kündigung mit Rückkaufswert und Prämienreduktion.
<agent>: Sehr gerne, ich sende Ihnen eine Übersicht an baumann@hotmail.com.
<customer>: Dann entscheide ich danach.
<agent>: Das klingt gut, Herr Baumann.""",
        "topics": ["12"],
        "summary": "Customer thinks about cancelling life insurance. Alternatives like premium reduction or premium-free continuation are shown."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer. Que voulez-vous savoir?
<customer>: J'ai acheté des bijoux à l'étranger. Sont-ils déjà assurés sur le chemin du retour ou seulement quand ils sont à la maison?
<agent>: Un bon point. Dans votre police WV-3507-W9, les objets de valeur sont assurés mondialement contre le vol, pour autant que certaines prescriptions de sécurité soient respectées.
<customer>: Quelles prescriptions?
<agent>: Par exemple, vous ne devez pas laisser les bijoux sans surveillance dans la voiture, et à l'hôtel vous devez utiliser le coffre-fort, s'il y en a un.
<customer>: Et si quelqu'un m'arrache le sac dans la rue?
<agent>: S'il s'agit d'un vol, ce serait en règle générale couvert, tant que vous n'avez pas agi avec négligence grave.
<customer>: D'accord, cela me rassure un peu. Alors j'espère que rien n'arrive du tout.
<agent>: Nous l'espérons aussi. Si vous voulez, vous pouvez nous envoyer après le retour une copie des justificatifs d'achat, pour que les valeurs soient actualisées dans le système.
<customer>: Je le fais.
<agent>: Parfait, Monsieur Keller.""",
        "topics": ["13"],
        "summary": "Customer asks about worldwide coverage of his newly acquired jewelry. The agent explains conditions and recommends submitting purchase receipts for updating."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. Another general question about Vaudoise.
<agent>: Good afternoon Mrs. Steiner, this is Pascal Tremblay. What's it about?
<customer>: I'm considering bundling all my insurance with a single provider. Before I do this with you, I want to know if I really only have one contact person in case of damage.
<agent>: A justified question. With us you receive a main contact who coordinates your files, even when various specialist departments are involved.
<customer>: Does that mean I don't have to tell everything multiple times?
<agent>: Exactly. Your main contact has access to relevant information and can internally involve the right places.
<customer>: Good, because this constant repetition annoys me with other providers.
<agent>: If you want, we can arrange a personal appointment where we go through your existing insurance and make a bundling offer.
<customer>: Send me a rough overview first before I invest time in an appointment.
<agent>: Of course, I'll send you an initial rough concept to steiner@gmail.com.
<customer>: Good, then we'll see further.
<agent>: Very gladly, Mrs. Steiner.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance with Vaudoise and asks about a central contact person. A rough concept is promised by email."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Simic. Je crains de ne pas avoir assuré certaines choses qui me sont importantes.
<agent>: Bonjour Monsieur Simic, ici Pascal Tremblay de Vaudoise. Quelles choses voulez-vous dire concrètement?
<customer>: Je travaille parfois depuis la maison et j'ai un équipement informatique coûteux dans le home office. Cela n'est mentionné nulle part explicitement.
<agent>: Je regarde dans vos documents avec la référence UD-2064-E3. Votre assurance ménage couvre en principe aussi les appareils de travail, mais seulement jusqu'à un certain montant.
<customer>: Et si la valeur est au-dessus?
<agent>: Alors nous aurions effectivement une lacune. Dans de nombreux cas, cela peut être comblé avec un module supplémentaire ou une solution d'affaires spéciale.
<customer>: Je ne veux pas soudainement entendre que c'est ma faute si on cambriole.
<agent>: C'est compréhensible. Je propose que nous saisissions la valeur approximative de votre équipement et que je calcule une couverture supplémentaire appropriée.
<customer>: Faites cela. Si c'est complètement excessif, je me cherche une autre solution.
<agent>: J'essaie de créer une offre équitable et transparente. Vous la recevrez à simic@gmail.com.
<customer>: D'accord.
<agent>: Merci, Monsieur Simic.""",
        "topics": ["2"],
        "summary": "Customer is unsure whether his home office equipment is sufficiently insured. The agent checks household contents coverage and creates an additional quote."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich wurde von einem Kollegen auf eine Kombi-Lösung bei der Vaudoise aufmerksam gemacht.
<agent>: Guten Tag Herr Simic, hier ist Marc Ducret. Meint Ihr Kollege vielleicht ein Paket aus Auto-, Hausrat- und Privathaftpflichtversicherung?
<customer>: Genau. Ich habe bisher nur die Fahrzeugversicherung bei Ihnen.
<agent>: Dann könnte sich ein Wechsel der anderen Versicherungen zu uns tatsächlich lohnen. Wir bieten bei Paketlösungen Rabatte an.
<customer>: Aber ich will keine Hochglanzverkaufsshow, nur klare Zahlen.
<agent>: Verstehe ich gut. Ich kann Ihnen auf Basis Ihrer aktuellen Situation eine nüchterne Vergleichsrechnung machen.
<customer>: Gut. Wenn sich nichts wirklich ändert, bleibe ich, wie ich bin.
<agent>: Das ist fair. Ich sende Ihnen eine Gegenüberstellung „Heute vs. Paketlösung" an simic@gmail.com.
<customer>: In Ordnung.
<agent>: Vielen Dank, dass Sie eine Paketlösung überhaupt in Betracht ziehen, Herr Simic.""",
        "topics": ["3"],
        "summary": "Customer is interested in a package solution with discounts but wants a clear numerical basis. A comparison calculation is created.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I'm calling again about my claim negotiation - I'm getting fed up.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner. I remember your case SV-6926-G8. What's currently the problem?
<customer>: I was promised on the phone that the deductible would be reduced, and now the original amount is in the letter again.
<agent>: Let me look at the notes... Indeed, it says here that a reduction was put in prospect, but apparently wasn't definitively approved yet.
<customer>: For me it came across like a commitment. I feel fooled.
<agent>: That was unfortunately formulated, I admit. I can now discuss the case directly with claims management.
<customer>: I expect you to keep your word - even if it was only "put in prospect".
<agent>: I understand your position. Can we do it like this: I'll get back to you by tomorrow with a final decision. Should the reduction be rejected, you'll receive a written justification.
<customer>: And if they write unclearly again, like before?
<agent>: I'll ask that the formulation be particularly understandable. And if you want, I'll additionally call you to explain everything personally.
<customer>: Alright. But this is your last chance, otherwise I'm gone.
<agent>: I take that very seriously, Mrs. Steiner.""",
        "topics": ["4"],
        "summary": "Customer is annoyed because a promised deductible reduction wasn't implemented in the letter. The case is clarified directly with claims management."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Schaden-Nachverfolgung.
<agent>: Guten Tag Herr Keller, hier ist Sarah Dürst. Um welchen Schaden geht es?
<customer>: SN-5675-E1, der Sturmschaden an meinem Dach. Ich weiss nicht, ob der Kostenvoranschlag akzeptiert wurde.
<agent>: Ich schaue… Ja, der Kostenvoranschlag der Firma wurde heute Morgen genehmigt.
<customer>: Aha, davon weiss ich nichts.
<agent>: Es hätte eine automatische E-Mail ausgelöst werden sollen. Offenbar hat das noch nicht geklappt.
<customer>: Das wundert mich nicht. Ich habe ohnehin das Gefühl, immer hinterherlaufen zu müssen.
<agent>: Es tut mir leid, dass dieser Eindruck entsteht. Ich sende Ihnen die Bestätigung gleich manuell zu.
<customer>: Gut. Und wann sehe ich das Geld?
<agent>: Die Auszahlung erfolgt nach Einreichen der Schlussrechnung. Bis dahin können Sie mit der Reparatur starten.
<customer>: Na gut, dann mache ich das so.
<agent>: Danke für Ihr Verständnis, Herr Keller.""",
        "topics": ["5"],
        "summary": "Customer waits for feedback on storm damage. The cost estimate is already approved, but the automatic notification didn't work; it's now sent manually."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller. I have a question about a premium invoice.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What's wrong with the invoice?
<customer>: Suddenly an annual payment is debited instead of a semi-annual one. I didn't change anything.
<agent>: Let me check your policy PZ-2949-B2. Here I see a changeover per contract renewal, where it was switched to annual payment by default.
<customer>: Without me signing anything?
<agent>: There was information in the renewal letter. If you don't agree with this, we can go back to semi-annual payment method.
<customer>: Yes, please. I can't just pay the whole amount at once.
<agent>: No problem. I'll reset the payment method, and the currently due invoice will be adjusted accordingly.
<customer>: Good. And please highlight such things more clearly next time.
<agent>: I'll gladly pass on your feedback, Mr. Keller.""",
        "topics": ["6"],
        "summary": "Customer notices a switch from semi-annual to annual payment method without his active involvement. The payment method is adjusted again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Berger. Ich wollte mich nach einer Unterstützung im Bereich Gesundheit erkundigen.
<agent>: Guten Tag Herr Berger, hier ist Yann Morel. Was genau interessiert Sie?
<customer>: Ich würde gerne an einem Präventionskurs für Rückentraining teilnehmen. Wird das teilweise übernommen?
<agent>: In Ihrer Police GS-8082-V9 gibt es ein Präventionsbudget, das für anerkannte Kurse genutzt werden kann.
<customer>: Wie hoch ist dieses Budget?
<agent>: Pro Jahr stehen Ihnen 300 Franken zur Verfügung, wenn der Kurs gewisse Kriterien erfüllt.
<customer>: Was für Kriterien?
<agent>: Der Anbieter muss zertifiziert sein, und der Kurs muss ein definiertes Programm umfassen, zum Beispiel über acht bis zehn Wochen.
<customer>: Okay, dann frage ich beim Kursanbieter nach einer Bestätigung.
<agent>: Genau, und schicken Sie uns danach die Kursbestätigung und Zahlungsbelege.
<customer>: Gut, dann mache ich das so.
<agent>: Perfekt, Herr Berger. So können Sie etwas für Ihren Rücken tun und gleichzeitig von der Versicherung profitieren.""",
        "topics": ["7"],
        "summary": "Customer inquires about prevention services for a back course. There is an annual prevention budget if course and provider meet certain criteria."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. Je voulais encore savoir quelque chose sur l'assistance panne.
<agent>: Bonjour Monsieur Berger, ici Yann Morel. Volontiers, que voulez-vous savoir?
<customer>: L'assistance panne vaut-elle aussi pour la voiture de ma partenaire si je conduis?
<agent>: Je regarde dans votre police PH-1780-E5. Dans votre cas, l'assistance panne est liée au véhicule, pas à la personne.
<customer>: Cela signifie que si je conduis avec sa voiture, je n'ai pas de chance?
<agent>: Pour cette voiture, votre assistance panne ne serait effectivement pas valable. Il faudrait une couverture propre ou une solution basée sur la personne.
<customer>: Eh bien, bravo. C'est sûrement écrit tout petit quelque part dans le texte, ou?
<agent>: C'est dans les conditions, oui, mais je comprends qu'on puisse facilement passer à côté.
<customer>: Franchement, cela m'énerve passablement.
<agent>: Je peux le comprendre. Si votre partenaire veut, nous pouvons examiner si une option assistance panne pour son véhicule ou une assistance basée sur les personnes en vaut la peine.
<customer>: Envoyez-moi d'abord des infos avant que je signe encore quelque chose.
<agent>: Très volontiers, je vous envoie un aperçu avec les deux possibilités à berger@gmail.com.""",
        "topics": ["8"],
        "summary": "Customer learns that his roadside assistance is vehicle-related and doesn't apply to his partner's car. He receives information about possible additional solutions."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I'm calling about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. How can I help?
<customer>: I've gone through your long policy and am honestly completely overwhelmed by the technical terms.
<agent>: Many people feel that way. Are there specific points that are unclear to you?
<customer>: For example, what exactly "new value compensation" means.
<agent>: That means that in case of damage we basically replace the replacement value of an equivalent new item, not just the time value.
<customer>: That at least sounds good. And what about things that are no longer manufactured?
<agent>: Then a comparable product or the monetary value is replaced.
<customer>: Could you perhaps send me a simplified summary of the most important points?
<agent>: Very gladly, I can create a simplified coverage sheet for you and send it to dvorak@hotmail.com.
<customer>: That would be great, then I finally understand what I actually bought.
<agent>: Very gladly, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is overwhelmed by technical terms in the property policy. The agent explains new value compensation and sends a simplified summary."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Worum geht es?
<customer>: Ich möchte wissen, ob sich ein Wechsel von Vollkasko auf Teilkasko lohnt. Mein Auto ist schon älter.
<agent>: Wie alt ist das Fahrzeug?
<customer>: Acht Jahre.
<agent>: Oft lohnt sich ab einem gewissen Fahrzeugalter tatsächlich ein Wechsel. Ich sehe in Ihrer Police FV-6623-H3, dass der Zeitwert schon deutlich gesunken ist.
<customer>: Und was spare ich ungefähr?
<agent>: Grob geschätzt könnten Sie rund 25 bis 30 Prozent der Prämie sparen.
<customer>: Und was verliere ich dafür?
<agent>: Sie wären bei selbstverschuldeten Kollisionen nicht mehr gedeckt, nur noch bei Ereignissen wie Diebstahl, Brand, Glasbruch, Elementarschäden und so weiter.
<customer>: Hm, ich denke, das Risiko kann ich eingehen.
<agent>: Wenn Sie möchten, kann ich eine Offerte für die Umstellung erstellen. Sie müssen diese dann nur noch bestätigen.
<customer>: Ja, schicken Sie sie mir.
<agent>: Gerne an keller@gmail.com.
<customer>: Genau.
<agent>: Dann mache ich das gleich, Herr Keller.""",
        "topics": ["10"],
        "summary": "Customer checks switching from comprehensive to partial coverage for an older vehicle. He receives a quote with premium savings and changed coverage."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe Fragen zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Was möchten Sie wissen?
<customer>: Ich plane eine Weltreise über mehrere Monate. Deckt meine aktuelle Police das überhaupt ab?
<agent>: Ich sehe mir Ihre Police RV-8954-C5 an. Sie ist primär für einzelne Reisen bis maximal 90 Tage ausgelegt.
<customer>: Meine Reise dauert aber mindestens sechs Monate.
<agent>: Dann reicht die aktuelle Police nicht aus. Wir müssten eine spezielle Langzeit-Reiselösung prüfen.
<customer>: Und warum steht das nicht klar irgendwo drauf?
<agent>: Es steht in den Bedingungen, aber ich gebe Ihnen recht, für längere Reisen ist das nicht sofort ersichtlich.
<customer>: Ganz ehrlich, das hätte ich fast übersehen. Ich wäre monatelang unterwegs gewesen und hätte gedacht, ich sei versichert.
<agent>: Gut, dass Sie vorher nachfragen. Ich kann Ihnen eine Offerte für eine Langzeitlösung erstellen oder, falls gewünscht, andere Optionen mit Ihnen besprechen.
<customer>: Schicken Sie mir eine Offerte, alles weitere sehe ich dann.
<agent>: Gerne, an roth@gmail.com.
<customer>: Ja, genau.
<agent>: Vielen Dank, Frau Roth.""",
        "topics": ["11"],
        "summary": "Customer plans a multi-month world trip. Her standard travel insurance only covers trips up to 90 days, so a long-term solution is created as a quote."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about Vaudoise.
<agent>: Good afternoon Mr. Baumann, this is Yann Morel. How can I help you?
<customer>: I'm wondering if I still need my existing insurance at all or if I'm over-insured.
<agent>: A justified question. We can do a so-called needs analysis.
<customer>: And does that mean you then want to sell me even more?
<agent>: Not necessarily. The goal is to find out what really fits your situation - that can also mean reducing something.
<customer>: That would be important to me.
<agent>: If you want, I'll send you a short questionnaire about household, income, family and assets. On this basis we can then review your coverage.
<customer>: Send it to baumann@gmail.com, but without marketing phrases.
<agent>: Understood, Mr. Baumann. I'll stick to the facts.""",
        "topics": ["1"],
        "summary": "Customer fears over-insurance. The agent offers a needs analysis via questionnaire where reductions are also possible.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Roth. I have another question about unmet insurance needs.
<agent>: Good afternoon Mrs. Roth, this is Sarah Dürst. What specifically is it about?
<customer>: I have a dog and I'm wondering if I need special liability insurance for that.
<agent>: In your personal liability insurance, pets are partially co-covered, depending on type and use. Let me quickly check this based on your file UD-4270-U4.
<customer>: He's a normal family dog, not a listed breed or anything.
<agent>: Then he would basically be co-insured, although there are maximum amounts and exclusions.
<customer>: And if he bites someone?
<agent>: Such damage would normally be covered, provided you meet the duty of care.
<customer>: Okay, that reassures me. So I don't need an extra policy?
<agent>: Not necessarily in your case. However, there are special animal owner policies with extended benefits if you want that.
<customer>: No, if it's sufficient like this, let's leave it at that.
<agent>: Alright, then there's no additional need in this area.""",
        "topics": ["2"],
        "summary": "Customer asks if her dog is sufficiently covered by personal liability insurance. There is basic coverage, so no additional policy is necessarily needed."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Steiner. J'ai une demande de vente.
<agent>: Bonjour Madame Steiner, ici Yann Morel. Qu'est-ce qui vous intéresse?
<customer>: J'ai pensé à souscrire une petite assurance vie pour la sécurité de mes enfants.
<agent>: C'est un sujet sensé. Avez-vous déjà une idée de la somme d'assurance souhaitée?
<customer>: Peut-être 50'000 francs par enfant.
<agent>: Nous pourrions établir une police avec une durée fixe jusqu'à un certain âge de vos enfants.
<customer>: Et qu'est-ce que cela me coûterait approximativement?
<agent>: Cela dépend de votre âge et de votre état de santé. En gros, nous sommes à quelques centaines de francs par an.
<customer>: Envoyez-moi s'il vous plaît une offre concrète. Je ne veux décider qu'une fois que j'ai vu les chiffres.
<agent>: Très volontiers, je vous envoie une offre avec deux variantes à steiner@gmail.com.
<customer>: Bien, alors je réfléchis à cela.
<agent>: Parfait, Madame Steiner.""",
        "topics": ["3"],
        "summary": "Customer is interested in a small life insurance for securing her children. She receives a quote with various variants."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverfolgung an – schon wieder.
<agent>: Guten Tag Frau Dvorak, hier ist Anna Meier. Es tut mir leid, dass Sie erneut anrufen müssen. Um welchen Schaden geht es?
<customer>: Um den Wasserschaden von letzter Woche, SN-4974-L3. Mir wurde ein Rückruf versprochen, aber niemand hat sich gemeldet.
<agent>: Ich sehe im System tatsächlich einen offenen Rückrufauftrag, der noch nicht erledigt wurde. Das hätte nicht passieren dürfen.
<customer>: So langsam glaube ich Ihnen gar nichts mehr.
<agent>: Ich verstehe Ihren Frust und entschuldige mich dafür. Ich kann Ihnen jetzt direkt Auskunft geben, wenn Sie möchten.
<customer>: Ja, bitte.
<agent>: Die Offerte des Handwerkers wurde genehmigt, Sie können mit der Reparatur beginnen. Die Zahlung erfolgt nach Eingang der Schlussrechnung.
<customer>: Warum sagt mir das niemand einfach rechtzeitig?
<agent>: Wir müssen unsere internen Abläufe verbessern, das ist offensichtlich. Ich werde den Vorgang als Beschwerde markieren.
<customer>: Tun Sie das. Vielleicht ändert sich dann etwas.
<agent>: Ich hoffe es auch, Frau Dvorak.""",
        "topics": ["5"],
        "summary": "Customer is annoyed because promised callbacks were missed. The approved claim is explained and the process is noted as a complaint."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Alonso. J'ai une question sur mes primes.
<agent>: Bonjour Madame Alonso, ici Marc Ducret. Que voulez-vous savoir?
<customer>: J'ai vu que j'ai un rabais pour plusieurs produits. Si j'annule une police, est-ce que je perds le rabais sur toutes les autres?
<agent>: Je vérifie votre police PZ-1231-V4. Votre rabais multiple dépend de trois produits de base: ménage, responsabilité civile et assurance véhicule.
<customer>: Et si je change l'assurance véhicule chez un autre fournisseur?
<agent>: Alors le rabais multiple serait réduit ou supprimé, ce qui peut conduire à des primes plus élevées sur les polices restantes.
<customer>: Donc à la fin, je ne fais peut-être aucun gain si je ne change qu'un contrat?
<agent>: Exactement, c'est pourquoi il vaut la peine de considérer l'effet global.
<customer>: Envoyez-moi s'il vous plaît une comparaison "avec assurance véhicule chez vous" et "sans".
<agent>: Très volontiers, je vous envoie cette comparaison à alonso@gmail.com.
<customer>: Alors je calcule tranquillement.
<agent>: C'est une très bonne idée, Madame Alonso.""",
        "topics": ["6"],
        "summary": "Customer wants to know how cancelling vehicle insurance affects her multiple discount. She receives a comparison of total premiums."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich habe eine Frage zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer. Worum geht es?
<customer>: Mein Zahnarzt hat mir eine Zahnreinigung empfohlen, die ziemlich teuer ist. Zahlt die Vaudoise etwas daran?
<agent>: In Ihrer Police GS-9392-W8 ist eine Beteiligung an Dentalhygiene-Leistungen bis zu einem jährlichen Höchstbetrag vorgesehen.
<customer>: Wie hoch ist der?
<agent>: Maximal 150 Franken pro Jahr.
<customer>: Das ist besser als nichts. Muss die Dentalhygienikerin speziell anerkannt sein?
<agent>: Ja, sie sollte bei einem anerkannten Berufsverband registriert sein. Das steht normalerweise auf der Rechnung.
<customer>: Gut, dann achte ich darauf.
<agent>: Reichen Sie uns die Rechnung einfach ein, und wir prüfen die Beteiligung.
<customer>: Alles klar, danke.
<agent>: Sehr gern, Herr Baumann.""",
        "topics": ["7"],
        "summary": "Customer asks about insurance contribution to professional teeth cleaning. There is an annual contribution provided the provider is recognized."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Berger. I want to ask a question about my roadside assistance.
<agent>: Hello Mr. Berger, this is Yann Morel. How can I help?
<customer>: If I'm traveling with a rental car, am I covered by my roadside assistance?
<agent>: In your policy PH-1780-E5, the coverage refers to your own vehicle with the registered license plate.
<customer>: So no?
<agent>: Exactly, your roadside assistance doesn't apply to a rental car. Most rental car providers have their own assistance services.
<customer>: Good to know. Then I need to look more carefully there.
<agent>: That's definitely recommended.
<customer>: Thanks for the clear answer.
<agent>: Very gladly, Mr. Berger.""",
        "topics": ["8"],
        "summary": "Customer inquires whether his roadside assistance also applies to rental cars. The coverage is vehicle-related and doesn't apply to rental vehicles."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I have a longer question about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. Tell me what concerns you.
<customer>: I recently renovated quite a bit and bought new appliances. I'm afraid I've overlooked something important.
<agent>: Then let's go through this systematically. Your policy HR-7227-U5 is currently issued for 70,000 francs household contents.
<customer>: That was before the renovations.
<agent>: Exactly. We could check it in five steps:
<agent>: First: We roughly record the value of your new furniture and appliances.
<customer>: That's certainly 15,000 to 20,000 francs.
<agent>: Second: We look at whether there are special individual pieces like designer items or antiques that should be listed separately.
<customer>: An antique table would be there.
<agent>: Third: We check whether the location of your risk has changed, for example through a move or major structural changes.
<customer>: No, the apartment is the same.
<agent>: Fourth: We calculate an adjusted insurance sum so you're not underinsured.
<customer>: And fifth?
<agent>: Fifth: We decide together whether additional modules like extended elemental damage or glass breakage make sense.
<customer>: Good, that sounds like a plan. Can you summarize this in writing for me?
<agent>: Very gladly, I'll send you a summary and a proposal for the new insurance sum to dvorak@hotmail.com.
<customer>: Thanks, then I'll go through everything in peace.
<agent>: Perfect, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is concerned about underinsurance after renovations and new purchases. A structured 5-point plan for adjusting property insurance is agreed upon.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe nochmals eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Was möchten Sie wissen?
<customer>: Ich überlege mir, die Versicherung komplett zu wechseln. Können Sie mir sagen, wie lange meine Kündigungsfrist ist?
<agent>: In Ihrer Police FV-6623-H3 ist eine Kündigung jeweils auf das Ende der Versicherungsperiode mit dreimonatiger Frist vorgesehen.
<customer>: Das heisst, ich bin noch fast ein Jahr gebunden?
<agent>: Ausser bei einem Schadenfall oder einer Prämienänderung – dann gibt es ein ausserordentliches Kündigungsrecht.
<customer>: Hm. Dann warte ich wohl ab, was mit den Prämien nächstes Jahr passiert.
<agent>: Das ist eine Möglichkeit. Wenn Sie möchten, kann ich Ihre Police auf Optimierungspotenzial prüfen, damit ein Wechsel vielleicht gar nicht nötig ist.
<customer>: Nein danke, im Moment will ich nur die Frist wissen.
<agent>: In Ordnung, Herr Keller. Dann bleibt es bei den genannten drei Monaten vor Ablauf.""",
        "topics": ["10"],
        "summary": "Customer inquires about cancellation period of his vehicle insurance because he considers switching. He leaves it at the information for now."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Noch eine Frage zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Gerne, was möchten Sie wissen?
<customer>: Deckt meine Police auch den Verlust meines Laptops auf Reisen?
<agent>: Ich sehe in Ihrer Police RV-8954-C5 eine Gepäckversicherung, allerdings mit einem Höchstbetrag pro Einzelgegenstand.
<customer>: Und wie hoch ist der?
<agent>: 2'000 Franken pro Gegenstand.
<customer>: Mein Laptop war teurer.
<agent>: Dann wäre im Schadenfall der Ersatz auf diesen Höchstbetrag begrenzt. Es gibt die Möglichkeit, besonders wertvolle Gegenstände separat zu versichern.
<customer>: Das ist ja wieder kompliziert. Aber gut, dann weiss ich Bescheid.
<agent>: Wenn Sie möchten, kann ich Ihnen Informationen zu einer separaten Elektronikversicherung schicken.
<customer>: Schicken Sie es, entscheiden werde ich später.
<agent>: Sehr gern, an roth@gmail.com.""",
        "topics": ["11"],
        "summary": "Customer asks if her laptop is fully covered while traveling. Luggage insurance has a maximum amount per item; a separate electronics insurance is mentioned as an option."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Weber. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Herr Weber, hier ist Anna Meier von der Vaudoise. Womit kann ich Ihnen helfen?
<customer>: Ich bin gerade umgezogen und frage mich, ob ich alle meine Policen aktualisieren muss.
<agent>: Das ist eine sehr wichtige Frage. Ein Umzug kann verschiedene Auswirkungen auf Ihre Versicherungen haben. Haben Sie Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 52-BH-3847-N2.
<agent>: Danke. Ich sehe hier eine Hausrat-, Privathaftpflicht- und Fahrzeugversicherung. Bei einem Umzug sollten wir mindestens die Adressen aktualisieren.
<customer>: Ändert sich dadurch auch die Prämie?
<agent>: Das kann durchaus sein, je nach Risikozone des neuen Wohnorts. Manchmal wird es günstiger, manchmal teurer.
<customer>: Können Sie das für mich prüfen und mir eine Übersicht schicken?
<agent>: Sehr gerne. Ich sende Ihnen eine Aufstellung aller notwendigen Änderungen an weber@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer inquires about updating his insurance policies after moving. The agent explains potential premium changes and offers to send a comprehensive overview."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Martin. J'ai l'impression qu'il me manque quelque chose dans mes assurances.
<agent>: Bonjour Madame Martin, ici Pascal Tremblay de Vaudoise. Qu'est-ce qui vous préoccupe?
<customer>: Je viens de commencer à travailler en freelance depuis la maison, et je me demande si mon équipement professionnel est couvert.
<agent>: C'est une excellente question. Votre police ménage standard couvre généralement l'équipement privé, mais pas nécessairement l'équipement professionnel.
<customer>: Et qu'est-ce que cela signifie concrètement? Mon ordinateur portable et mon matériel de bureau ne sont pas assurés?
<agent>: Cela dépend de la valeur et de l'usage. Pour un usage professionnel intensif, nous recommandons souvent une extension spéciale.
<customer>: Pouvez-vous me faire une offre pour cela? Je ne veux pas me retrouver sans protection.
<agent>: Bien sûr, je vous prépare une proposition pour une couverture équipement professionnel à domicile. Je vous l'envoie à martin@hotmail.com.""",
        "topics": ["2"],
        "summary": "Customer working as freelancer from home discovers potential coverage gap for professional equipment. Agent prepares special coverage proposal.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Thompson. I'm interested in expanding my insurance coverage with Vaudoise.
<agent>: Hello Mr. Thompson, this is Sarah Dürst from Vaudoise. What type of coverage are you looking for?
<customer>: I just bought a motorcycle and I need insurance for it. I already have car insurance with you.
<agent>: Excellent! Since you're already our customer, we can offer attractive package discounts. What type of motorcycle did you purchase?
<customer>: It's a touring bike, mainly for weekend trips and holidays.
<agent>: For touring bikes, I'd recommend comprehensive coverage including roadside assistance for longer trips. Would you like me to prepare a quote?
<customer>: Yes, please. But I want to see different options - basic and comprehensive coverage.
<agent>: Perfect. I'll prepare both variants and send them to thompson@gmail.com. You can then choose what fits your needs and budget best.""",
        "topics": ["3"],
        "summary": "Existing customer wants motorcycle insurance for his new touring bike. Agent prepares quotes for both basic and comprehensive coverage options.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Müller. Ich bin sehr unzufrieden mit der Bearbeitung meines Schadensfalls.
<agent>: Guten Tag Frau Müller, hier ist Marc Ducret. Es tut mir leid, dass Sie unzufrieden sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruchschaden, Referenz SV-7429-X1. Die Schadensregulierung zieht sich schon seit Wochen hin.
<agent>: Lassen Sie mich den Fall aufrufen... Ich sehe, dass noch zusätzliche Belege angefordert wurden. Haben Sie diese eingereicht?
<customer>: Ja, schon vor zwei Wochen! Aber seither höre ich nichts mehr. Das ist doch unmöglich.
<agent>: Sie haben recht, das ist zu lange. Ich sehe die Belege im System, aber sie wurden noch nicht bearbeitet. Das hätte schneller gehen müssen.
<customer>: Ich brauche das Geld dringend, um die Schäden zu reparieren. Wann kann ich endlich mit einer Entscheidung rechnen?
<agent>: Ich priorisiere Ihren Fall sofort und sorge dafür, dass die Bearbeitung bis spätestens übermorgen abgeschlossen ist. Sie erhalten eine schriftliche Bestätigung.""",
        "topics": ["4"],
        "summary": "Customer frustrated with delayed burglary claim processing despite submitting required documents weeks ago. Agent prioritizes the case for immediate completion."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Dubois. J'appelle pour suivre mon dossier sinistre.
<agent>: Bonjour Monsieur Dubois, ici Luca Steiner de Vaudoise. Quel est le numéro de référence?
<customer>: SN-8856-P4. Il s'agit des dégâts de grêle sur ma voiture.
<agent>: Je vois votre dossier. L'expert a terminé son évaluation et l'offre de règlement a été préparée.
<customer>: Et pourquoi ne l'ai-je pas encore reçue?
<agent>: Elle devait vous être envoyée hier. Permettez-moi de vérifier... Il semble y avoir eu un retard dans l'envoi postal.
<customer>: C'est toujours pareil avec vous. On doit constamment relancer.
<agent>: Je comprends votre frustration. Je vous envoie immédiatement l'offre par email et je vérifie que le courrier soit aussi expédié aujourd'hui.
<customer>: Faites donc cela. Et j'espère que le montant est correct cette fois.
<agent>: L'expert a évalué tous les dommages visibles. Si vous n'êtes pas d'accord, nous pouvons discuter d'une contre-expertise.""",
        "topics": ["5"],
        "summary": "Customer follows up on hail damage claim. Settlement offer was delayed in postal delivery, agent sends it immediately by email."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Johnson. I have a question about my premium payment.
<agent>: Good morning Mrs. Johnson, this is Nora Widmer from Vaudoise. How can I assist you?
<customer>: I received a bill that seems much higher than usual. I'm wondering if there's been a mistake.
<agent>: Let me check your account. Could you provide me with your policy number?
<customer>: It's PZ-4712-M9.
<agent>: Thank you. I see there was indeed a premium adjustment due to a claim you made last year, which affected your no-claims bonus.
<customer>: But I thought my bonus protection would prevent that?
<agent>: Your bonus protection covers one claim per year, but you had two claims in the same period, so the second one affected your premium.
<customer>: Nobody told me about this! I would have handled the smaller claim myself if I had known.
<agent>: I understand your concern. Let me send you a detailed breakdown showing how your premium was calculated, so you can see exactly what happened.""",
        "topics": ["6"],
        "summary": "Customer questions higher premium bill. Agent explains impact of multiple claims on no-claims bonus and offers detailed calculation breakdown."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Schmidt. Ich habe Fragen zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Schmidt, hier ist Anna Meier. Womit kann ich Ihnen helfen?
<customer>: Mein Physiotherapeut hat mir eine längere Behandlung empfohlen, und ich möchte wissen, was übernommen wird.
<agent>: Schauen wir in Ihre Police GS-5578-K2. Sie haben eine Zusatzversicherung mit Physiotherapie-Deckung.
<customer>: Gibt es eine Begrenzung der Anzahl Sitzungen?
<agent>: Pro Jahr sind 30 Sitzungen gedeckt, vorausgesetzt sie sind ärztlich verordnet.
<customer>: Mein Arzt empfiehlt 35 Sitzungen. Was passiert mit den zusätzlichen fünf?
<agent>: Die können über die Grundversicherung laufen oder Sie zahlen sie selbst. Ich empfehle, zuerst die Kostengutsprache für alle 35 Sitzungen zu beantragen.
<customer>: Können Sie mir die nötigen Formulare schicken?
<agent>: Gerne. Ich sende Ihnen alle Unterlagen an schmidt@gmail.com.""",
        "topics": ["7"],
        "summary": "Customer inquires about physiotherapy coverage limits. Agent explains 30 sessions are covered and helps with authorization process for additional sessions."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Petit. Mon auto est tombée en panne sur l'autoroute.
<agent>: Bonjour Madame Petit, ici Yann Morel de l'assistance Vaudoise. Êtes-vous en sécurité?
<customer>: Oui, je suis sur la bande d'arrêt d'urgence avec les feux de détresse allumés.
<agent>: Parfait. Où vous trouvez-vous exactement?
<customer>: Sur l'A1 direction Genève, juste après la sortie de Morges.
<agent>: Votre numéro de police est PH-9341-R7, c'est bien cela?
<customer>: Oui, c'est correct. Le moteur s'est arrêté d'un coup et ne redémarre plus.
<agent>: J'organise immédiatement un dépanneur. Il devrait arriver dans 30 à 40 minutes maximum.
<customer>: Et si la réparation n'est pas possible sur place?
<agent>: Alors on remorque votre véhicule vers un garage partenaire. Les frais sont couverts par votre assistance routière.
<customer>: Parfait, merci. J'attends alors le dépanneur.
<agent>: Il vous appellera quelques minutes avant d'arriver, Madame Petit.""",
        "topics": ["8"],
        "summary": "Customer's car breaks down on highway. Roadside assistance is dispatched with full coverage for towing and repair services."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Williams. I have a question about my property insurance.
<agent>: Good afternoon Mr. Williams, this is Pascal Tremblay from Vaudoise. What can I help you with?
<customer>: We're planning to install solar panels on our roof. Does this affect our property insurance?
<agent>: That's a great question. Solar panel installations can indeed impact your coverage. Let me check your policy HR-6684-L5.
<customer>: Do I need to inform you before the installation?
<agent>: Yes, it's important to notify us as it increases the value of your property and changes the risk profile slightly.
<customer>: Will this increase my premium significantly?
<agent>: Usually the increase is minimal because solar panels are well-secured installations. But the coverage increase protects your investment.
<customer>: That makes sense. What information do you need from me?
<agent>: I'll send you a simple form to complete with installation details and value. Then we can adjust your policy accordingly.""",
        "topics": ["9"],
        "summary": "Customer planning solar panel installation asks about property insurance impact. Agent explains notification requirements and minimal premium increase.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Hofmann. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Frau Hofmann, hier ist Sarah Dürst. Worum geht es?
<customer>: Meine Tochter hat gerade den Führerschein gemacht. Kann ich sie in meine Versicherung aufnehmen?
<agent>: Ja, das ist möglich. Allerdings wird sich die Prämie erhöhen, da Fahranfänger ein höheres Risiko darstellen.
<customer>: Um wie viel ungefähr?
<agent>: Das hängt vom Alter und anderen Faktoren ab. Für Ihre Police FV-7823-D6 würde ich schätzen, etwa 40-60% Aufschlag.
<customer>: Das ist aber teuer! Gibt es Alternativen?
<agent>: Wir könnten eine separate Police für Ihre Tochter eröffnen oder schauen, ob es günstigere Fahranfänger-Programme gibt.
<customer>: Schicken Sie mir bitte beide Varianten zur Ansicht.
<agent>: Sehr gerne, ich erstelle Ihnen eine Vergleichsrechnung und sende sie an hofmann@gmail.com.""",
        "topics": ["10"],
        "summary": "Customer wants to add newly licensed daughter to car insurance. Agent explains premium increase and offers comparison between adding to existing policy vs separate coverage."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Brown. I'm calling about my travel insurance.
<agent>: Hello Ms. Brown, this is Luca Steiner from Vaudoise. How can I help you?
<customer>: I'm planning a ski trip to the Alps next month. Does my travel insurance cover winter sports?
<agent>: Let me check your policy RV-1247-Q3... Yes, you have winter sports coverage included, but with certain conditions.
<customer>: What kind of conditions?
<agent>: The coverage applies to marked ski slopes and recognized winter sports areas. Off-piste skiing requires additional coverage.
<customer>: I'm only planning to ski on regular slopes. What about ski equipment?
<agent>: Your policy covers ski equipment up to 1,500 francs per person against theft or damage.
<customer>: That should be sufficient. Do I need to do anything special before the trip?
<agent>: No special preparation needed. Just make sure to keep receipts for any equipment rentals or purchases for potential claims.""",
        "topics": ["11"],
        "summary": "Customer confirms travel insurance coverage for upcoming ski trip. Agent explains winter sports coverage conditions and equipment protection limits."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Zimmermann. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Zimmermann, hier ist Marc Ducret. Wie kann ich Ihnen helfen?
<customer>: Ich habe geheiratet und möchte meine Frau als Begünstigte eintragen lassen.
<agent>: Herzlichen Glückwunsch zur Hochzeit! Das können wir gerne anpassen. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-8834-F7.
<agent>: Danke. Möchten Sie Ihre Frau als alleinige Begünstigte eintragen oder prozentual aufteilen?
<customer>: Als alleinige Begünstigte. Gibt es dabei etwas zu beachten?
<agent>: Bei einer Änderung der Begünstigung empfehlen wir auch zu prüfen, ob die Versicherungssumme noch angemessen ist.
<customer>: Das ist ein guter Punkt. Können Sie mir eine Einschätzung geben?
<agent>: Gerne. Ich sende Ihnen das Änderungsformular und eine Bedarfsanalyse für die Versicherungssumme an zimmermann@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to update life insurance beneficiary after marriage. Agent processes change and offers to review adequacy of insurance amount."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Leroy. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Madame Leroy, ici Anna Meier de Vaudoise. Que puis-je faire pour vous?
<customer>: J'ai hérité de bijoux de famille et je voudrais savoir s'ils sont automatiquement couverts.
<agent>: Les nouveaux objets de valeur ne sont pas automatiquement couverts. Il faut les déclarer et les faire évaluer.
<customer>: Comment procède-t-on pour l'évaluation?
<agent>: Vous devez faire appel à un expert bijoutier agréé qui établira une estimation officielle de la valeur.
<customer>: Et cela coûte cher?
<agent>: L'expertise coûte généralement entre 100 et 200 francs selon la complexité, mais c'est indispensable pour la couverture.
<customer>: D'accord. Pouvez-vous me donner les coordonnées d'experts agréés?
<agent>: Bien sûr, je vous envoie une liste d'experts dans votre région à leroy@gmail.com.""",
        "topics": ["13"],
        "summary": "Customer inherited family jewelry and asks about insurance coverage. Agent explains evaluation requirement by certified expert and provides expert list.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Wagner. Ich habe eine allgemeine Frage zu Vaudoise.
<agent>: Guten Tag Frau Wagner, hier ist Pascal Tremblay. Womit kann ich Ihnen behilflich sein?
<customer>: Ich überlege, alle meine Versicherungen bei einem Anbieter zu bündeln. Welche Vorteile bietet das?
<agent>: Eine Bündelung bringt mehrere Vorteile: Rabatte, einfachere Verwaltung und einen zentralen Ansprechpartner.
<customer>: Wie hoch sind die Rabatte normalerweise?
<agent>: Je nach Produktkombination können Sie zwischen 5 und 15 Prozent auf die Gesamtprämie sparen.
<customer>: Das klingt interessant. Ich habe derzeit Auto-, Hausrat- und Haftpflichtversicherung bei verschiedenen Anbietern.
<agent>: Das wären perfekte Kandidaten für eine Bündelung. Soll ich Ihnen eine unverbindliche Vergleichsrechnung erstellen?
<customer>: Ja, gerne. Aber ohne Verkaufsdruck bitte.
<agent>: Selbstverständlich. Sie erhalten nur Zahlen und Fakten zur eigenen Entscheidung. Ich sende die Berechnung an wagner@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance policies with Vaudoise. Agent explains benefits including discounts and offers comparison calculation."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Davis. I think I might have a gap in my insurance coverage.
<agent>: Hello Mr. Davis, this is Nora Widmer from Vaudoise. What makes you think there might be a gap?
<customer>: I started a small consulting business from home and I'm not sure if my professional liability is covered.
<agent>: That's an important concern. Personal liability insurance typically doesn't cover professional activities. Let me check your current coverage.
<customer>: My policy number is UD-5591-H8.
<agent>: I see you have personal liability but no professional liability insurance. For consulting work, you'd need a separate business liability policy.
<customer>: I was afraid of that. How urgent is this?
<agent>: Very urgent. If a client makes a claim against your consulting services, you wouldn't be protected without proper coverage.
<customer>: Can you prepare a quote for professional liability insurance?
<agent>: Absolutely. I'll prepare a quote specifically for consulting services and send it to davis@hotmail.com today.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for new consulting business. Personal liability doesn't cover professional activities, so separate business liability insurance is needed urgently."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Becker. Ich interessiere mich für eine neue Versicherung.
<agent>: Guten Tag Herr Becker, hier ist Sarah Dürst von der Vaudoise. Welche Art von Versicherung schwebt Ihnen vor?
<customer>: Ich kaufe ein Wohnmobil für den Ruhestand und brauche dafür eine passende Versicherung.
<agent>: Glückwunsch zum neuen Wohnmobil! Dafür gibt es spezielle Campingfahrzeug-Versicherungen mit erweiterten Leistungen.
<customer>: Was ist denn anders als bei einer normalen Fahrzeugversicherung?
<agent>: Zum Beispiel Campingzubehör-Versicherung, erweiterte Pannenhilfe in ganz Europa und Schutz bei längeren Standzeiten.
<customer>: Das klingt sinnvoll. Ich plane längere Reisen durch Europa.
<agent>: Dann ist eine umfassende Europa-Deckung besonders wichtig. Soll ich Ihnen verschiedene Deckungsoptionen zusammenstellen?
<customer>: Ja, bitte. Schicken Sie mir eine detaillierte Offerte mit verschiedenen Varianten.
<agent>: Sehr gerne. Ich erstelle Ihnen passende Angebote für Ihr Wohnmobil und sende sie an becker@gmail.com.""",
        "topics": ["3"],
        "summary": "Customer needs insurance for new motorhome for retirement travels. Agent explains specialized camping vehicle insurance with European coverage options."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Moreau. Je suis mécontent du règlement de mon sinistre.
<agent>: Bonjour Monsieur Moreau, ici Marc Ducret. Je suis désolé d'apprendre votre mécontentement. De quel sinistre s'agit-il?
<customer>: Dégâts d'eau dans ma cave, référence SV-2847-K9. Vous refusez une partie des dommages.
<agent>: Laissez-moi consulter le dossier... Je vois qu'une partie a été classée comme dommages préexistants.
<customer>: C'est ridicule! L'eau venait de la canalisation du voisin, pas de chez moi.
<agent>: Je comprends votre position. L'expert a constaté que certains dégâts étaient antérieurs à la fuite du voisin.
<customer>: Je ne peux pas accepter cela. Je veux une contre-expertise.
<agent>: C'est votre droit. Nous pouvons organiser une seconde expertise par un expert indépendant.
<customer>: Faites-le. Et cette fois, je veux être présent lors de l'inspection.
<agent>: Bien sûr, vous serez informé de tous les rendez-vous. Je lance la procédure immédiatement.""",
        "topics": ["4"],
        "summary": "Customer disputes water damage claim settlement where part was classified as pre-existing damage. Second independent expert evaluation is requested."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Taylor. I'm calling for an update on my claim.
<agent>: Good afternoon Mrs. Taylor, this is Luca Steiner from Vaudoise. What's your claim reference number?
<customer>: SN-3765-Q1. It's for the storm damage to my garden shed.
<agent>: Let me check... I see that the adjuster's report was completed and approved yesterday.
<customer>: Finally! When will I receive the settlement?
<agent>: The payment has been processed and should reach your account within 2-3 business days.
<customer>: Great. Will you also cover the cleanup costs for the debris?
<agent>: Yes, the cleanup costs are included in the settlement amount as they were part of the original damage assessment.
<customer>: Perfect. I was worried I'd have to pay for that separately.
<agent>: No, everything is covered as agreed. You'll receive a detailed settlement statement by email today.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on storm damage claim. Settlement including cleanup costs has been processed and will arrive within days."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Fischer. Ich habe eine Frage zu meiner Prämienrechnung.
<agent>: Guten Tag Herr Fischer, hier ist Anna Meier von der Vaudoise. Was ist unklar bei Ihrer Rechnung?
<customer>: Ich zahle seit Jahren pünktlich, aber bekomme nie einen Rabatt für treue Kunden.
<agent>: Lassen Sie mich Ihre Police PZ-6739-N4 prüfen... Sie haben bereits den maximalen Schadenfreiheitsrabatt.
<customer>: Aber andere Versicherer bieten zusätzliche Treueboni an.
<agent>: Das stimmt. Wir haben andere Vorteile wie kostenlose Serviceleistungen und bevorzugte Schadensbearbeitung für langjährige Kunden.
<customer>: Das ist mir nicht bekannt. Können Sie mir diese Leistungen auflisten?
<agent>: Gerne. Ich sende Ihnen eine Übersicht aller Zusatzleistungen, die Sie als Bestandskunde erhalten.
<customer>: Das wäre hilfreich. Vielleicht übersehe ich ja etwas.
<agent>: Ich bin sicher, da sind einige Leistungen dabei, die Sie noch nicht kannten. Die Übersicht geht an fischer@gmail.com.""",
        "topics": ["6"],
        "summary": "Long-term customer asks about loyalty discounts. Agent explains existing maximum discount and additional customer benefits for loyal clients."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Girard. J'ai des questions sur mes prestations santé.
<agent>: Bonjour Madame Girard, ici Nora Widmer. En quoi puis-je vous aider?
<customer>: Mon médecin m'a prescrit des séances de naturopathie. Est-ce que c'est couvert?
<agent>: Laissez-moi vérifier votre police GS-4493-T8... Vous avez une couverture médecines alternatives avec certaines conditions.
<customer>: Quelles conditions exactement?
<agent>: Le praticien doit être reconnu par l'ASCA ou le RME, et il y a un plafond annuel de 1000 francs.
<customer>: Et comment savoir si mon naturopathe est reconnu?
<agent>: Vous pouvez vérifier sur les sites web ASCA ou RME, ou simplement demander à votre praticien ses certifications.
<customer>: D'accord. Et si je dépasse les 1000 francs?
<agent>: Alors les frais supplémentaires seraient à votre charge. Je vous envoie la liste des praticiens reconnus dans votre région pour référence.""",
        "topics": ["7"],
        "summary": "Customer inquires about naturopathy coverage. Agent explains recognition requirements and annual limits for alternative medicine practitioners."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Anderson. I need emergency roadside assistance.
<agent>: Hello Mr. Anderson, this is Yann Morel from Vaudoise assistance. Are you in a safe location?
<customer>: Yes, I'm in a parking lot. My car won't start and I have an important meeting in an hour.
<agent>: I understand the urgency. What's your location and policy number?
<customer>: I'm at the shopping center in Lausanne, policy PH-7741-S3.
<agent>: Perfect, I can dispatch a technician immediately. They should arrive within 20-25 minutes.
<customer>: What if they can't fix it on site?
<agent>: If it can't be repaired, we can provide a replacement vehicle so you can make your meeting.
<customer>: You have replacement cars available?
<agent>: Yes, your policy includes replacement vehicle service for mechanical breakdowns. The technician will arrange it if needed.
<customer>: That's a relief. Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs urgent roadside assistance before important meeting. Quick dispatch arranged with replacement vehicle option if repair isn't possible."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Koch. Ich habe eine Frage zur Gebäudeversicherung.
<agent>: Guten Tag Frau Koch, hier ist Pascal Tremblay von der Vaudoise. Wobei kann ich helfen?
<customer>: Wir haben einen Swimming Pool bauen lassen. Muss das in der Versicherung angemeldet werden?
<agent>: Das ist eine wichtige Frage. Ein Pool erhöht den Gebäudewert und sollte definitiv gemeldet werden.
<customer>: Wird dadurch die Prämie viel teurer?
<agent>: Die Erhöhung ist normalerweise moderat, da Pools fest installiert und gegen die meisten Risiken gut geschützt sind.
<customer>: Was ist mit der Haftpflicht? Wenn jemand im Pool verunglückt?
<agent>: Das wäre über Ihre Privathaftpflichtversicherung gedeckt, vorausgesetzt Sie haben den Pool ordnungsgemäß gesichert.
<customer>: Können Sie beide Policen entsprechend anpassen?
<agent>: Gerne. Ich erstelle Ihnen die Anpassungen und sende sie zur Prüfung an koch@gmail.com.""",
        "topics": ["9"],
        "summary": "Customer reports new swimming pool construction. Agent explains building insurance adjustment and liability coverage requirements."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Bernard. Ma voiture a été volée cette nuit.
<agent>: Bonjour Monsieur Bernard, ici Sarah Dürst de Vaudoise. Je suis désolée d'apprendre cela. Avez-vous déjà contacté la police?
<customer>: Oui, j'ai déposé plainte ce matin. Le numéro de plainte est 2024-445-891.
<agent>: Parfait. Votre numéro de police est FV-5529-J6, c'est bien cela?
<customer>: Oui. Qu'est-ce que je dois faire maintenant?
<agent>: Je vais ouvrir un dossier sinistre immédiatement. Vous devez nous envoyer une copie de la plainte et nous donner tous les détails du vol.
<customer>: La voiture était fermée à clé devant chez moi. Il n'y avait rien d'anormal.
<agent>: D'accord. Avez-vous encore tous les clés en votre possession?
<customer>: Oui, toutes les clés étaient à la maison. Comment ça se passe pour le remboursement?
<agent>: Nous attendons d'abord que la police termine son enquête, puis nous procédons selon la valeur actuelle de votre véhicule.""",
        "topics": ["10"],
        "summary": "Customer reports car theft that occurred overnight. Agent opens claim file and explains process including police investigation and current value assessment."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Ms. Wilson. I have a question about my travel insurance.
<agent>: Good afternoon Ms. Wilson, this is Marc Ducret from Vaudoise. What would you like to know?
<customer>: I'm pregnant and wondering if this affects my travel insurance for an upcoming trip.
<agent>: Congratulations! Pregnancy does have some implications for travel insurance. Let me check your policy RV-8822-D7.
<customer>: I'm in my second trimester and planning to travel to Italy next month.
<agent>: For pregnancy-related coverage, there are specific conditions. Normal pregnancy isn't considered an illness, but complications could be covered.
<customer>: What if I need medical attention while abroad?
<agent>: Emergency medical care is covered, but routine pregnancy check-ups during travel are not included in standard coverage.
<customer>: Should I consider additional coverage?
<agent>: I'd recommend discussing with your doctor first about travel safety, then we can assess if additional pregnancy-related coverage would be beneficial.""",
        "topics": ["11"],
        "summary": "Pregnant customer inquires about travel insurance coverage. Agent explains emergency vs routine care coverage and suggests medical consultation first."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Richter. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Richter, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich bin arbeitslos geworden und kann mir die Prämien nicht mehr leisten. Was sind meine Optionen?
<agent>: Das tut mir leid zu hören. Es gibt mehrere Möglichkeiten: Prämienbefreiung, Reduktion der Versicherungssumme oder temporäre Aussetzung.
<customer>: Was bedeutet Prämienbefreiung genau?
<agent>: Bei nachgewiesener Arbeitslosigkeit können wir die Prämienzahlung für bis zu 12 Monate aussetzen, ohne dass der Vertrag verfällt.
<customer>: Das wäre ideal. Welche Unterlagen brauchen Sie?
<agent>: Eine Bescheinigung des RAV und einen Nachweis über das Arbeitslosengeld. Der Schutz bleibt während dieser Zeit bestehen.
<customer>: Perfekt. Wo kann ich diese Unterlagen einreichen?
<agent>: Ich sende Ihnen das entsprechende Formular und die Anweisungen an richter@gmail.com.""",
        "topics": ["12"],
        "summary": "Unemployed customer can't afford life insurance premiums. Agent explains premium waiver option for unemployment with continued coverage.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. Roberts. I have a question about my valuables insurance.
<agent>: Hello Mrs. Roberts, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm going on vacation and want to take some jewelry with me. Are they covered while traveling?
<agent>: Your valuables policy WV-7734-X2 includes worldwide coverage, but with certain security requirements while traveling.
<customer>: What kind of security requirements?
<agent>: Items should not be left unattended in vehicles, and hotel safes should be used when available. There are also coverage limits per item.
<customer>: What if the hotel doesn't have a safe?
<agent>: Then you should keep valuable items with you at all times or consider leaving very expensive pieces at home for this trip.
<customer>: That makes sense. Is there anything else I should know?
<agent>: Take photos of the jewelry before traveling and keep receipts. This helps with any potential claims.""",
        "topics": ["13"],
        "summary": "Customer asks about jewelry coverage while traveling. Agent explains worldwide coverage with security requirements and documentation recommendations."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Neumann. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Frau Neumann, hier ist Pascal Tremblay. Was beschäftigt Sie?
<customer>: Meine Nachbarin hatte einen Wasserschaden und war wochenlang ohne Heizung. Bin ich dagegen versichert?
<agent>: Das ist eine wichtige Überlegung. Schauen wir in Ihre Hausratversicherung HR-9966-L1, ob zusätzliche Lebenshaltungskosten gedeckt sind.
<customer>: Was sind zusätzliche Lebenshaltungskosten?
<agent>: Wenn Ihre Wohnung unbewohnbar wird, zahlen wir Hotelkosten oder Miete für eine Ersatzwohnung für eine begrenzte Zeit.
<customer>: Wie lange ist diese begrenzte Zeit?
<agent>: In Ihrer Police sind bis zu 12 Monate gedeckt, je nach Umfang der Schäden und Reparaturdauer.
<customer>: Das beruhigt mich. Muss ich bestimmte Hotels wählen?
<agent>: Nein, aber die Kosten müssen angemessen sein. Wir erstatten bis zur Höhe Ihrer normalen Wohnkosten plus einem Aufschlag.
<customer>: Gut zu wissen. Danke für die Erklärung.""",
        "topics": ["1"],
        "summary": "Customer asks about coverage for alternative accommodation after hearing neighbor's water damage story. Agent explains additional living costs coverage terms."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Fabre. Je pense avoir un besoin d'assurance non couvert.
<agent>: Bonjour Monsieur Fabre, ici Sarah Dürst. Qu'est-ce qui vous préoccupe?
<customer>: Je fais de la photographie professionnelle et mon équipement coûte très cher. Mon assurance ménage ne suffit pas.
<agent>: Effectivement, l'équipement professionnel nécessite souvent une couverture spécialisée. Quelle est la valeur approximative?
<customer>: Environ 25'000 francs en appareils photos, objectifs et équipement d'éclairage.
<agent>: Pour cette valeur, nous recommandons une assurance équipement professionnel avec couverture mondiale.
<customer>: Mondiale? Pourquoi?
<agent>: Pour un photographe, l'équipement voyage beaucoup. Il faut une protection contre le vol, les dommages et la perte, même à l'étranger.
<customer>: Cela me semble logique. Pouvez-vous me faire une offre?
<agent>: Bien sûr, je vous prépare une proposition pour assurance équipement professionnel photographique. Je l'envoie à fabre@gmail.com.""",
        "topics": ["2"],
        "summary": "Professional photographer needs specialized equipment insurance beyond standard household coverage. Agent prepares worldwide professional equipment proposal."
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Clarke. I'm interested in business insurance for my new company.
<agent>: Good morning Mr. Clarke, this is Marc Ducret from Vaudoise. Congratulations on your new business! What type of company are you starting?
<customer>: It's a small IT consulting firm. I'll be working mostly with corporate clients on software projects.
<agent>: For IT consulting, you'll need professional liability insurance, general liability, and possibly cyber liability coverage.
<customer>: Cyber liability? What's that for?
<agent>: It protects against data breaches, cyber attacks, and privacy violations. Very important for IT companies handling client data.
<customer>: That makes sense. How much does this typically cost for a small firm?
<agent>: For a startup IT consulting firm, we're typically looking at 1,500 to 3,000 francs annually for a comprehensive package.
<customer>: That seems reasonable. Can you prepare a detailed quote?
<agent>: Absolutely. I'll create a tailored business insurance package for your IT consulting firm and send it to clarke@gmail.com.""",
        "topics": ["3"],
        "summary": "Entrepreneur needs business insurance for new IT consulting firm. Agent explains professional, general, and cyber liability coverage needs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Weber. Ich bin extrem verärgert über die Schadensbearbeitung.
<agent>: Guten Tag Frau Weber, hier ist Luca Steiner. Es tut mir leid zu hören, dass Sie verärgert sind. Was ist passiert?
<customer>: Sturmschaden am Dach, Referenz SV-5641-M2. Die Reparatur wurde abgelehnt wegen angeblicher Vorschäden.
<agent>: Lassen Sie mich den Fall prüfen... Ich sehe, dass der Gutachter Altersschwäche der Dachziegel festgestellt hat.
<customer>: Das Dach ist erst fünf Jahre alt! Das ist doch kein Alter.
<agent>: Sie haben recht, das ist sehr jung für ein Dach. Haben Sie noch Garantieunterlagen vom Dachdecker?
<customer>: Natürlich! Die habe ich auch schon eingereicht, aber niemand hat darauf reagiert.
<agent>: Das hätte beachtet werden müssen. Ich lasse den Fall von unserem Bauschadenexperten neu bewerten.
<customer>: Endlich mal jemand, der zuhört! Wann kann ich mit einer Antwort rechnen?
<agent>: Bis Ende der Woche haben Sie eine neue Einschätzung. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["4"],
        "summary": "Customer frustrated about roof damage claim rejection due to alleged pre-existing damage on 5-year-old roof. Case referred to construction damage expert for reevaluation."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Rousseau. Je voudrais un point sur mon sinistre.
<agent>: Bonjour Madame Rousseau, ici Anna Meier de Vaudoise. Quel est votre numéro de référence?
<customer>: SN-7788-V5. Il s'agit du cambriolage de mon appartement il y a trois semaines.
<agent>: Je vois votre dossier. L'enquête de police est terminée et nous avons reçu le rapport officiel.
<customer>: Parfait. Et maintenant?
<agent>: Nous finalisons l'inventaire des objets volés. Avez-vous d'autres preuves d'achat à nous envoyer?
<customer>: Non, je vous ai tout transmis. Quand vais-je être indemnisée?
<agent>: Le règlement sera effectué dans les 5 jours ouvrables. Vous recevrez d'abord un décompte détaillé.
<customer>: Très bien. Y aura-t-il une franchise à déduire?
<agent>: Oui, votre police prévoit une franchise de 500 francs pour les cambriolages.
<customer>: D'accord, je m'y attendais. Merci pour ces nouvelles rassurantes.""",
        "topics": ["5"],
        "summary": "Customer gets positive update on burglary claim. Police investigation complete, settlement will be processed within 5 business days with standard deductible."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Turner. I have a billing question.
<agent>: Hello Mr. Turner, this is Pascal Tremblay from Vaudoise. What's your billing concern?
<customer>: I switched to annual payments instead of quarterly, but I was charged a processing fee.
<agent>: Let me check your account PZ-8844-R7... I see the payment frequency change and the associated fee.
<customer>: I wasn't told there would be a fee for this change.
<agent>: You're right, that should have been communicated clearly. The fee is typically waived for voluntary changes to less frequent payments.
<customer>: So the fee shouldn't have been charged?
<agent>: Correct. I'll reverse the processing fee and it should appear as a credit on your next statement.
<customer>: Thank you. Will this happen again if I make other changes?
<agent>: No, changes that reduce our administrative costs, like yours, shouldn't incur fees. I'll make sure this is noted in your file.""",
        "topics": ["6"],
        "summary": "Customer charged unexpected fee for switching to annual payments. Agent reverses fee and clarifies that beneficial payment changes shouldn't incur costs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Maurer. Ich habe Fragen zu Gesundheitsleistungen.
<agent>: Guten Tag Herr Maurer, hier ist Nora Widmer. Womit kann ich helfen?
<customer>: Mein Arzt hat mir Akupunktur verschrieben. Wird das übernommen?
<agent>: Schauen wir in Ihre Police GS-3377-B9... Sie haben eine Zusatzversicherung mit Komplementärmedizin-Deckung.
<customer>: Wie funktioniert die Kostenerstattung?
<agent>: Die Behandlung muss von einem anerkannten Therapeuten durchgeführt werden, dann erstatten wir 70% der Kosten.
<customer>: Bis zu welchem jährlichen Betrag?
<agent>: Ihr Jahresbudget für Komplementärmedizin beträgt 800 Francs.
<customer>: Und wie weiss ich, ob mein Therapeut anerkannt ist?
<agent>: Fragen Sie nach der ASCA- oder RME-Registrierung oder geben Sie mir die Praxisdaten, dann prüfe ich das für Sie.
<customer>: Die Praxis ist in Bern, Dr. Chen, Akupunkturzentrum Bern.
<agent>: Ich prüfe das und melde mich noch heute bei Ihnen zurück.""",
        "topics": ["7"],
        "summary": "Customer asks about acupuncture coverage. Agent explains 70% reimbursement with annual limit and offers to verify therapist recognition status."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Phillips. I need roadside assistance.
<agent>: Good afternoon Mrs. Phillips, this is Yann Morel from Vaudoise assistance. What's your situation?
<customer>: I have a flat tire and I don't have a spare. I'm on the highway near Bern.
<agent>: Are you in a safe location off the roadway?
<customer>: Yes, I'm in a rest area with my hazard lights on.
<agent>: Perfect. Your policy PH-2255-K8 includes tire service. I can send a mobile tire service to replace your flat tire.
<customer>: How long will that take?
<agent>: The tire service should reach you within 45 minutes. They'll have common tire sizes on the truck.
<customer>: What if they don't have my tire size?
<agent>: Then we'll tow you to the nearest tire shop and cover the costs. Your policy includes this service.
<customer>: Great, that takes the stress away. Thank you for the quick help.""",
        "topics": ["8"],
        "summary": "Customer has flat tire on highway with no spare. Mobile tire service dispatched with backup towing option if needed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Vogel. Es geht um meine Wohngebäudeversicherung.
<agent>: Guten Tag Herr Vogel, hier ist Sarah Dürst. Was kann ich für Sie tun?
<customer>: Wir planen einen Wintergarten anzubauen. Muss das versichert werden?
<agent>: Ja, Anbauten erhöhen die Gebäudeversicherungssumme und sollten gemeldet werden.
<customer>: Der Wintergarten kostet etwa 50.000 Franken. Wie stark steigt dadurch die Prämie?
<agent>: Bei Ihrer Police HR-4488-W6 würde das etwa 120-150 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist weniger als erwartet. Wann muss ich das melden?
<agent>: Idealerweise vor Baubeginn, spätestens bei Fertigstellung. So ist der Anbau von Anfang an mitversichert.
<customer>: Gibt es besondere Auflagen für Wintergärten?
<agent>: Meist nicht, solange er nach den Bauvorschriften errichtet wird. Senden Sie mir die Baupläne, dann prüfe ich das genauer.""",
        "topics": ["9"],
        "summary": "Customer planning winter garden addition asks about building insurance requirements. Agent explains coverage increase and timing for reporting construction."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Blanc. J'ai des questions sur mon assurance auto.
<agent>: Bonjour Madame Blanc, ici Marc Ducret de Vaudoise. Que voulez-vous savoir?
<customer>: Mon fils va bientôt avoir 18 ans et passer son permis. Comment l'assurer?
<agent>: Il y a plusieurs options: l'ajouter à votre police existante ou lui faire une police séparée.
<customer>: Qu'est-ce qui est le plus avantageux?
<agent>: Cela dépend de votre bonus actuel. L'ajouter peut être moins cher, mais risque d'affecter votre bonus en cas d'accident.
<customer>: Et avec une police séparée?
<agent>: Il commence avec un bonus jeune conducteur, mais vos polices restent indépendantes.
<customer>: Peut-être que c'est plus sûr. Pouvez-vous calculer les deux variantes?
<agent>: Bien sûr, je vous prépare une comparaison des coûts et avantages de chaque solution. Je l'envoie à blanc@gmail.com.""",
        "topics": ["10"],
        "summary": "Mother asks about insuring her soon-to-be 18-year-old son. Agent explains options of adding to existing policy vs separate coverage with pros and cons.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Green. I have a travel insurance question.
<agent>: Good morning Mr. Green, this is Luca Steiner from Vaudoise. What would you like to know?
<customer>: I'm planning a business trip that might extend into a vacation. Does my travel insurance cover both purposes?
<agent>: Let me check your policy RV-6655-F4... You have standard travel insurance which covers both business and leisure travel.
<customer>: What if the trip gets extended unexpectedly for business reasons?
<agent>: Extensions for business reasons are generally covered, but there's a maximum trip duration limit in your policy.
<customer>: What's my limit?
<agent>: Your policy covers trips up to 180 days. If you need longer coverage, we'd need to arrange extended travel insurance.
<customer>: That should be plenty. Is there anything special I need to do for combined business-leisure trips?
<agent>: No special requirements, the coverage is the same regardless of the purpose of your travel.""",
        "topics": ["11"],
        "summary": "Customer asks about travel insurance for combined business-leisure trip. Standard coverage applies to both purposes with 180-day maximum duration."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Lang. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Frau Lang, hier ist Anna Meier. Wie kann ich Ihnen helfen?
<customer>: Meine finanzielle Situation hat sich verbessert und ich möchte die Versicherungssumme erhöhen.
<agent>: Das freut mich für Sie! Schauen wir uns Ihre Police LV-7711-Q3 an. Um wie viel möchten Sie erhöhen?
<customer>: Von 150.000 auf 250.000 Franken.
<agent>: Das ist eine substanzielle Erhöhung. Dafür ist normalerweise eine neue Gesundheitsprüfung erforderlich.
<customer>: Auch wenn ich schon Kunde bin?
<agent>: Ja, bei Erhöhungen über 50.000 Franken ist eine Gesundheitsprüfung Standard, unabhängig von der bestehenden Kundenbeziehung.
<customer>: Wie läuft das ab?
<agent>: Zuerst füllen Sie einen Gesundheitsfragebogen aus, möglicherweise folgt dann eine ärztliche Untersuchung.
<customer>: Schicken Sie mir die Unterlagen zu. Ich bin gesund und mache mir keine Sorgen.
<agent>: Sehr gerne. Die Unterlagen für die Erhöhung gehen an lang@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to increase life insurance sum due to improved financial situation. Agent explains health examination requirements for substantial increases."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Stone. I have a question about my valuables insurance.
<agent>: Hello Mr. Stone, this is Pascal Tremblay from Vaudoise. How can I help you?
<customer>: I collect vintage watches and some have appreciated significantly in value. Should I update my coverage?
<agent>: Absolutely! Appreciated items should definitely be revalued for proper coverage. When was your last appraisal?
<customer>: About three years ago. Some pieces have doubled in value since then.
<agent>: Then an update is overdue. Underinsurance could result in reduced payouts in case of loss.
<customer>: What's the process for updating values?
<agent>: You'll need fresh appraisals from certified watch experts. We can provide a list of recognized appraisers.
<customer>: That makes sense. Will my premiums increase significantly?
<agent>: Premiums will adjust to reflect the new values, but it's better to pay slightly more for proper coverage than risk major losses.
<customer>: You're right. Please send me the appraiser list and update forms.""",
        "topics": ["13"],
        "summary": "Vintage watch collector needs to update valuables coverage after significant appreciation. Agent emphasizes importance of current appraisals and offers appraiser list.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Huber. Ich habe eine grundsätzliche Frage zu Versicherungen.
<agent>: Guten Tag Herr Huber, hier ist Sarah Dürst. Was beschäftigt Sie?
<customer>: Ich lebe seit kurzem allein nach der Scheidung und frage mich, welche Versicherungen ich wirklich brauche.
<agent>: Das ist eine wichtige Überprüfung nach einer Lebensveränderung. Welche Versicherungen haben Sie derzeit?
<customer>: Auto, Hausrat und Privathaftpflicht. Meine Ex-Frau hatte immer die Übersicht.
<agent>: Das ist eine solide Grundausstattung. Haben Sie Kinder oder Unterhaltsverpflichtungen?
<customer>: Zwei Kinder, ja. Ich zahle Unterhalt.
<agent>: Dann könnte eine Lebensversicherung sinnvoll sein, um die Unterhaltszahlungen abzusichern.
<customer>: Daran habe ich nicht gedacht. Können Sie mir eine Bedarfsanalyse machen?
<agent>: Gerne erstelle ich Ihnen eine individuelle Bedarfsanalyse basierend auf Ihrer neuen Lebenssituation.""",
        "topics": ["1"],
        "summary": "Recently divorced customer reviews insurance needs for new life situation with children and alimony obligations. Agent offers comprehensive needs analysis.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Dupont. Je crois avoir une lacune dans mes assurances.
<agent>: Bonjour Madame Dupont, ici Marc Ducret. Quelle lacune suspectez-vous?
<customer>: J'ai commencé à faire de la location Airbnb dans ma maison secondaire. Est-ce que c'est couvert?
<agent>: C'est une excellente question. La location courte durée n'est généralement pas couverte par l'assurance habitation standard.
<customer>: Qu'est-ce que cela signifie concrètement?
<agent>: En cas de dommages causés par des locataires Airbnb, votre assurance pourrait refuser la prise en charge.
<customer>: C'est embêtant! Que puis-je faire?
<agent>: Nous avons des extensions spéciales pour location courte durée qui couvrent ces risques spécifiques.
<customer>: Et pour la responsabilité civile si un locataire se blesse?
<agent>: Cela aussi nécessite une couverture étendue. Je vous prépare une offre complète pour activité Airbnb.
<customer>: Faites cela rapidement, j'ai déjà des réservations pour le mois prochain.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for Airbnb rental activity in secondary home. Standard home insurance doesn't cover short-term rentals; special extension needed urgently.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Harris. I'm interested in additional insurance products.
<agent>: Good afternoon Mrs. Harris, this is Nora Widmer from Vaudoise. What type of additional coverage interests you?
<customer>: I'm thinking about legal protection insurance. I've been having some disputes with contractors lately.
<agent>: Legal protection can be very valuable, especially if you frequently deal with service providers. What type of disputes are you facing?
<customer>: Mainly construction and renovation issues. Poor workmanship and contract disagreements.
<agent>: Legal protection insurance would cover consultation with lawyers and court costs for such disputes.
<customer>: Does it cover ongoing disputes or only new ones after the policy starts?
<agent>: Only disputes that arise after the policy effective date. Ongoing issues wouldn't be covered.
<customer>: That's fair. How much does legal protection typically cost?
<agent>: For comprehensive legal protection, you're looking at around 300-400 francs annually, depending on coverage limits.""",
        "topics": ["3"],
        "summary": "Customer interested in legal protection insurance due to contractor disputes. Agent explains coverage for future disputes only and provides cost estimates."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Keller. Ich bin wirklich sauer auf die Schadensregulierung.
<agent>: Guten Tag Frau Keller, hier ist Luca Steiner. Es tut mir leid, dass Sie verärgert sind. Was ist geschehen?
<customer>: Glasschaden am Auto, Referenz SV-9922-T7. Der Schaden wurde abgelehnt wegen angeblicher Manipulation.
<agent>: Das ist ein schwerwiegender Vorwurf. Lassen Sie mich den Fall genau prüfen.
<customer>: Ich habe einen Steinschlag gehabt, das ist alles! Warum sollte ich das manipulieren?
<agent>: Ich verstehe Ihre Verärgerung. Können Sie mir den Hergang nochmals schildern?
<customer>: Ich fuhr hinter einem Lastwagen, plötzlich Knall in der Scheibe. Ganz normal halt.
<agent>: Haben Sie Zeugen oder war jemand anders im Auto?
<customer>: Meine Nachbarin sass neben mir. Sie kann das bestätigen.
<agent>: Das ist wichtig. Ich lasse den Fall von einem anderen Sachbearbeiter neu bewerten und berücksichtige die Zeugenaussage.
<customer>: Endlich jemand, der mir glaubt! Wann höre ich etwas?""",
        "topics": ["4"],
        "summary": "Customer angry about glass damage claim rejection due to alleged manipulation. Agent reopens case with new adjuster and includes witness testimony."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Mitchell. I'm calling about my claim status.
<agent>: Hello Mr. Mitchell, this is Anna Meier from Vaudoise. What's your claim reference?
<customer>: SN-4433-L6. It's for water damage from a burst pipe last month.
<agent>: Let me check your file... I see the restoration work has been completed and final invoices received.
<customer>: Yes, everything's done. When can I expect final payment?
<agent>: The final payment has been approved and will be transferred to your account tomorrow morning.
<customer>: Excellent. Will there be any adjustment to the original estimate?
<agent>: Actually yes, the final amount is about 800 francs less than estimated because some damaged items could be repaired instead of replaced.
<customer>: That's good news. Will I receive a detailed final statement?
<agent>: Yes, you'll get a complete breakdown of all costs and payments by email today.
<customer>: Perfect. Thank you for the efficient handling of this claim.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on water damage claim. Final payment approved with costs lower than estimated due to successful repairs rather than replacements."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Graf. Ich verstehe meine Prämienrechnung nicht.
<agent>: Guten Tag Herr Graf, hier ist Pascal Tremblay. Was ist unklar an Ihrer Rechnung?
<customer>: Es gibt verschiedene Abzüge und Zuschläge, ich kenne mich nicht aus.
<agent>: Gerne erkläre ich Ihnen die Rechnung Schritt für Schritt. Haben Sie sie vor sich?
<customer>: Ja. Da steht etwas von einem Schadenfreiheitsrabatt und einem Selbstbehalt-Bonus.
<agent>: Der Schadenfreiheitsrabatt belohnt Sie dafür, dass Sie keine Schäden hatten. Je länger schadensfrei, desto höher der Rabatt.
<customer>: Und der Selbstbehalt-Bonus?
<agent>: Den erhalten Sie, weil Sie einen höheren Selbstbehalt gewählt haben. Das reduziert Ihre Grundprämie.
<customer>: Verstehe. Und warum ist dann noch ein Zuschlag da?
<agent>: Welcher Zuschlag genau? Können Sie mir die Zeile vorlesen?
<customer>: "Regionale Anpassung +15%".
<agent>: Das ist ein regionaler Zuschlag aufgrund höherer Schadenkosten in Ihrer Gegend. Der ist leider unvermeidlich.""",
        "topics": ["6"],
        "summary": "Customer confused about premium calculation details. Agent explains no-claims discount, deductible bonus, and regional adjustment factors step by step."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Leroy. J'ai des questions sur ma couverture santé.
<agent>: Bonjour Monsieur Leroy, ici Sarah Dürst. En quoi puis-je vous aider?
<customer>: Mon dentiste propose un nouveau traitement coûteux et je veux savoir ce qui est pris en charge.
<agent>: De quel type de traitement s'agit-il?
<customer>: Des implants dentaires. Cela coûte environ 8000 francs.
<agent>: Regardons votre police GS-6688-U7... Vous avez une couverture dentaire avec certaines limitations.
<customer>: Quelles limitations?
<agent>: Les implants sont couverts à hauteur de 75% maximum 5000 francs par an pour les traitements dentaires majeurs.
<customer>: Donc je recevrais 5000 francs maximum?
<agent>: Exactement. Et il faut d'abord obtenir une autorisation de coûts avant de commencer le traitement.
<customer>: Comment faire cette demande?
<agent>: Votre dentiste doit nous envoyer un plan de traitement détaillé avec devis. Nous évaluons ensuite la nécessité médicale.""",
        "topics": ["7"],
        "summary": "Customer asks about dental implant coverage. Policy covers 75% up to 5000 francs annually for major dental work with prior authorization required."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Cooper. I need emergency roadside assistance.
<agent>: Good morning Mrs. Cooper, this is Yann Morel from Vaudoise assistance. What's your emergency?
<customer>: My car battery is dead in a parking garage. I think I left the lights on overnight.
<agent>: That happens to everyone! Are you in a safe, accessible location for our service vehicle?
<customer>: Yes, it's a public parking garage with good access.
<customer>: Can you give me your exact location and policy number?
<agent>: I'm at the Westside shopping center in Bern, underground parking level 1. Policy PH-5577-N9.
<agent>: Perfect. I can dispatch a mobile battery service immediately. They'll have jump cables and replacement batteries if needed.
<customer>: How quickly can they get here?
<agent>: For parking garage locations, usually 15-20 minutes. They'll call you when they arrive at the entrance.
<customer>: Excellent service! Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs jump start for dead battery in shopping center parking garage. Mobile battery service dispatched with 15-20 minute response time."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Gross. Frage zur Gebäudeversicherung.
<agent>: Guten Tag Herr Gross, hier ist Marc Ducret. Womit kann ich helfen?
<customer>: Wir installieren eine Wärmepumpe. Ändert das etwas an der Versicherung?
<agent>: Eine Wärmepumpe ist eine wertvolle Gebäudeinstallation und sollte mitversichert werden.
<customer>: Die Anlage kostet 25.000 Franken. Um wie viel steigt die Prämie?
<agent>: Bei Ihrer Police HR-1199-X3 würde das etwa 60-80 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist moderat. Gibt es besondere Risiken bei Wärmepumpen?
<agent>: Hauptrisiken sind Frost-, Elektronik- und Vandalismusschäden. Letztere sind leider nicht selten.
<customer>: Vandalismusschäden? Bei einer Wärmepumpe?
<agent>: Ja, die Außengeräte werden leider manchmal mutwillig beschädigt. Deshalb ist eine umfassende Deckung wichtig.
<customer>: Dann sollten wir das auf jeden Fall machen. Schicken Sie mir die Unterlagen.""",
        "topics": ["9"],
        "summary": "Customer installing heat pump asks about building insurance implications. Agent explains coverage importance including vandalism protection for outdoor units."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Vincent. Question sur mon assurance véhicule.
<agent>: Bonjour Madame Vincent, ici Luca Steiner de Vaudoise. Que voulez-vous savoir?
<customer>: Je vais acheter une voiture électrique. Est-ce que cela change quelque chose à mon assurance?
<agent>: Les voitures électriques ont quelques spécificités. Elles nécessitent souvent une couverture étendue pour la batterie.
<customer>: Pourquoi la batterie spécifiquement?
<agent>: Les batteries coûtent très cher à remplacer et ont des risques particuliers comme la surchauffe ou les dégâts dus au sel de route.
<customer>: Et pour l'assistance routière?
<agent>: Nous recommandons une assistance étendue car les pannes électriques nécessitent des dépanneurs spécialisés.
<customer>: Cela va coûter beaucoup plus cher?
<agent>: Environ 10-15% de plus qu'une voiture classique, mais c'est justifié par les technologies spécifiques.
<customer>: D'accord. Préparez-moi une offre complète pour véhicule électrique.""",
        "topics": ["10"],
        "summary": "Customer buying electric vehicle asks about insurance differences. Agent explains battery coverage and specialized roadside assistance needs with modest premium increase."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baker. I have a travel insurance inquiry.
<agent>: Good afternoon Mr. Baker, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm planning a hiking trip in the Himalayas. Does my travel insurance cover high-altitude activities?
<agent>: That's an adventure! Let me check your policy RV-3399-H8... You have standard travel insurance which has altitude restrictions.
<customer>: What kind of restrictions?
<agent>: Standard coverage applies up to 4,500 meters altitude. Above that, you need specialized high-altitude coverage.
<customer>: The trek goes up to 5,500 meters. What are my options?
<agent>: We can arrange an extension for high-altitude activities, including helicopter evacuation if needed.
<customer>: Helicopter evacuation? That sounds expensive.
<agent>: It is, but essential at those altitudes where normal rescue isn't possible. The extension is about 200 francs for a two-week trip.
<customer>: That's reasonable for peace of mind. Please arrange the high-altitude coverage.""",
        "topics": ["11"],
        "summary": "Customer planning Himalayan trek needs high-altitude travel insurance extension above 4,500 meters. Coverage includes specialized evacuation services."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Schmid. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Frau Schmid, hier ist Pascal Tremblay. Wie kann ich helfen?
<customer>: Mein Mann ist verstorben und ich muss die Leistung beantragen.
<agent>: Mein herzliches Beileid, Frau Schmid. Ich helfe Ihnen gerne bei allen Formalitäten.
<customer>: Welche Unterlagen brauchen Sie?
<agent>: Den Sterbeausweis, eine Kopie des Ehescheins und ein ausgefülltes Leistungsformular.
<customer>: Wie lange dauert die Bearbeitung normalerweise?
<agent>: Nach Eingang aller Unterlagen etwa 10-14 Tage. In besonderen Härtefällen können wir eine Vorauszahlung leisten.
<customer>: Das wäre hilfreich, da ich hohe Bestattungskosten habe.
<agent>: Das verstehe ich. Ich sende Ihnen alle Formulare und organisiere eine Vorauszahlung von 50% der Versicherungssumme.
<customer>: Vielen Dank für Ihr Verständnis und Ihre Hilfe.
<agent>: Das ist selbstverständlich in dieser schweren Zeit.""",
        "topics": ["12"],
        "summary": "Widow applies for life insurance benefits after husband's death. Agent offers compassionate processing with 50% advance payment to help with funeral costs."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Taylor. I have a question about my valuables coverage.
<agent>: Hello Ms. Taylor, this is Sarah Dürst from Vaudoise. What would you like to know?
<customer>: I'm getting married and received expensive wedding gifts. How do I add them to my insurance?
<agent>: Congratulations on your wedding! New valuable items should be reported within 30 days of acquisition.
<customer>: What constitutes a valuable item that needs special coverage?
<agent>: Generally items worth more than 2,000 francs like jewelry, art, or collectibles should be individually listed.
<customer>: I received a diamond necklace and some silver pieces. Do I need appraisals?
<agent>: For items over 5,000 francs, we require professional appraisals. For others, purchase receipts or gift documentation suffice.
<customer>: The necklace is worth about 8,000 francs. Can you recommend an appraiser?
<agent>: Certainly, I'll send you a list of certified jewelry appraisers in your area along with the coverage update forms.""",
        "topics": ["13"],
        "summary": "Newlywed needs to add expensive wedding gifts to valuables coverage. Agent explains reporting requirements and appraisal needs for high-value items.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Wolf. Ich habe eine grundlegende Frage zu Versicherungen.
<agent>: Guten Tag Herr Wolf, hier ist Marc Ducret. Womit kann ich Ihnen helfen?
<customer>: Ich ziehe bald ins Ausland und frage mich, was mit meinen Schweizer Versicherungen passiert.
<agent>: Das hängt davon ab, ob es ein vorübergehender oder dauerhafter Umzug ist und wohin Sie gehen.
<customer>: Ich gehe für mindestens fünf Jahre nach Deutschland für einen Job.
<agent>: Bei einem längerfristigen Umzug nach Deutschland können die meisten Versicherungen nicht einfach fortgeführt werden.
<customer>: Auch nicht die Lebensversicherung?
<agent>: Lebensversicherungen können oft fortgeführt werden, aber Sachversicherungen wie Auto und Hausrat müssen normalerweise gekündigt werden.
<customer>: Was ist mit meinen Rabatten und der Schadenfreiheit?
<agent>: Die Schadenfreiheit können wir Ihnen bescheinigen für die Verwendung bei deutschen Versicherern.
<customer>: Das ist gut zu wissen. Können Sie mir eine komplette Übersicht machen?
<agent>: Sehr gerne. Ich erstelle Ihnen eine detaillierte Auswanderer-Checkliste für alle Ihre Policen.""",
        "topics": ["1"],
        "summary": "Customer moving to Germany for work asks about insurance implications. Agent explains different rules for life vs property insurance and offers emigration checklist."
    },
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
        "suggested_topics": ["1"],
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
        "suggested_topics": ["2"],
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
        "suggested_topics": ["2"],
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
    },
{
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe eine allgemeine Frage zu meinen Versicherungen bei der Vaudoise.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Womit kann ich Ihnen helfen?
<customer>: Ich habe so viele verschiedene Policen, dass ich langsam den Überblick verliere. Können Sie mir sagen, was aktuell alles bei mir versichert ist?
<agent>: Natürlich. Dann starte ich am besten einen Gesamtüberblick. Haben Sie bitte kurz Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 45-AN-1295-M8.
<agent>: Vielen Dank. Einen Moment… ich sehe hier eine Hausrat-, eine Fahrzeug- und eine Reiseversicherung. Dazu noch eine kleine Lebensversicherung.
<customer>: Und wie sieht es mit einer Rechtsschutzversicherung aus? Ich dachte, ich hätte eine.
<agent>: Ich sehe im System keinen aktiven Rechtsschutzvertrag. Wir könnten prüfen, ob das für Sie sinnvoll wäre.
<customer>: Hm, das überrascht mich. Ich war sicher, dass ich eine habe. Das ärgert mich gerade ein bisschen.
<agent>: Das verstehe ich gut. Wenn Sie möchten, kann ich Ihnen eine kurze Zusammenstellung inkl. Offerte für eine Rechtsschutzversicherung per E-Mail schicken.
<customer>: Ja, tun Sie das bitte. Aber ich entscheide danach in Ruhe. Keine automatische Aktivierung!
<agent>: Selbstverständlich, es handelt sich nur um eine unverbindliche Offerte. Ist die E-Mail-Adresse dvorak@gmail.com noch aktuell?
<customer>: Ja, die stimmt.
<agent>: Perfekt, dann erhalten Sie im Laufe des Tages eine Übersicht über Ihre bestehenden Policen und einen separaten Vorschlag für die Rechtsschutzversicherung.
<customer>: Gut, danke. Dann warte ich darauf.
<agent>: Sehr gerne, Frau Dvorak. Wenn danach noch Fragen offen sind, können Sie uns jederzeit wieder anrufen.""",
        "topics": ["1"],
        "summary": "Customer wants a complete overview of her existing insurance policies and discovers that no legal protection insurance is present. She receives an overview and a non-binding quote.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Frau Dvorak. Ich habe das Gefühl, dass ich bei der Vaudoise nicht alles versichert habe, was ich eigentlich brauche.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Welche Situation beschäftigt Sie konkret?
<customer>: Wir haben kürzlich eine kleine Ferienwohnung gekauft, und mir ist aufgefallen, dass diese nirgends explizit erwähnt ist.
<agent>: Verstehe. Dann schauen wir uns Ihre Policen an. Könnten Sie mir bitte Ihre Kundennummer oder eine Policennummer geben?
<customer>: Die Policennummer ist UD-5715-K7.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung aktuell nur auf Ihre Hauptwohnung läuft. Die Ferienwohnung ist tatsächlich nicht eingeschlossen.
<customer>: Das ist genau das, was ich befürchtet habe. Wenn dort etwas passiert, stehe ich dann komplett ohne Schutz da?
<agent>: Für Schäden vor Ort, ja, aktuell wäre dort keine Deckung. Wir können das Objekt aber relativ einfach in Ihre Hausratversicherung integrieren oder separat versichern.
<customer>: Warum hat mir das niemand gesagt, als ich angerufen habe, bevor wir gekauft haben?
<agent>: Es tut mir leid, wenn das damals nicht klar kommuniziert wurde. Ich kann Ihren Fall intern vermerken, damit wir das überprüfen.
<customer>: Ich bin ehrlich gesagt ziemlich verärgert. Das ist doch Ihr Job, mich auf solche Lücken hinzuweisen.
<agent>: Ich verstehe Ihren Ärger sehr gut. Als Sofortmassnahme könnte ich Ihnen eine provisorische Deckung ab heute einrichten, damit Sie nicht länger ohne Schutz sind. Die definitive Police würden wir Ihnen dann schriftlich zustellen.
<customer>: Gut, dann machen Sie das bitte. Aber ich möchte keine versteckten Zusatzkosten.
<agent>: Selbstverständlich. Ich sende Ihnen noch heute eine transparente Offerte mit allen Prämien und Leistungen. Erst wenn Sie unterschreiben, wird die Police definitiv.
<customer>: In Ordnung, dann warte ich auf die Unterlagen. Wenn mir etwas komisch vorkommt, melde ich mich wieder.
<agent>: Das ist absolut in Ordnung. Vielen Dank für Ihre Offenheit, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer discovers that her new holiday apartment is not insured, is annoyed, and receives provisional coverage as well as a transparent quote to close the coverage gap.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Simic. I'm interested in additional insurance with Vaudoise.
<agent>: Good afternoon Mr. Simic, this is Nora Widmer. Nice that you're contacting us. What did you have in mind?
<customer>: I bought a new electric car and I'm wondering if I need something special for it.
<agent>: Congratulations on the new car! Do you drive the vehicle mainly privately or also for business?
<customer>: Only privately, but quite a lot. And I heard that batteries are very expensive if something happens to them.
<agent>: That's correct. We have a special module for electric vehicles that covers battery damage and extends assistance services.
<customer>: Sounds interesting. Can you give me an approximate idea of what this would cost me per year?
<agent>: If I base this on your current vehicle insurance with policy number VK-8002-K3, the additional module would be around 120 francs per year.
<customer>: Hmm. I honestly expected less.
<agent>: I understand. We could check whether you want optimizations on the deductible or other coverage to keep the overall premium stable.
<customer>: No, I don't want to tinker around everywhere. Just send me an offer, then I'll decide.
<agent>: Gladly. To which email address may I send the quote? I still have simic@gmail.com.
<customer>: Yes, that's correct. But please without automatic salutation "Dear Family", I hate that.
<agent>: Alright, I'll note that. You'll receive a personal quote addressed only to you.
<customer>: Good, then let's wait and see what comes.
<agent>: Very gladly, Mr. Simic. If you have questions afterwards or want to conclude directly, just contact us.""",
        "topics": ["3"],
        "summary": "Customer is interested in expanding his vehicle insurance for a new electric car. He has a quote sent to him but doesn't want any adjustments to other coverage for now.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. Il s'agit de mon sinistre en cours chez Vaudoise, et je ne suis pas satisfaite.
<agent>: Bonjour Madame Roth, ici Anna Meier. Je regrette d'apprendre que vous n'êtes pas satisfaite. De quel sinistre s'agit-il?
<customer>: Il s'agit des dégâts d'eau dans mon appartement, numéro de référence SV-5385-I9. Vous ne voulez me rembourser qu'une partie des coûts.
<agent>: Un moment, j'ouvre le dossier... Oui, je vois qu'une partie des coûts a été classée comme entretien non assuré.
<customer>: C'est exactement ce que je trouve injuste. J'ai tout fait entretenir régulièrement. Maintenant je me retrouve avec plusieurs milliers de francs à ma charge.
<agent>: Je comprends que ce soit frustrant. Selon l'expertise, les conduites étaient déjà fortement corrodées, ce qui constitue un défaut préexistant.
<customer>: Je ne peux pas accepter cela ainsi. Je n'ai jamais reçu d'écrit disant que quelque chose n'était pas en ordre.
<agent>: Ce que je peux faire pour vous: nous pouvons faire procéder à une seconde évaluation par un expert indépendant. Cela peut cependant prendre quelques jours.
<customer>: Franchement, j'en ai assez de ces "quelques jours". Cela traîne depuis des semaines.
<agent>: Je peux le comprendre. Alternativement, nous pourrions examiner un montant partiel comme paiement de complaisance, sans reconnaissance d'obligation légale.
<customer>: Alors, soit vous prenez en charge davantage, soit je vais voir l'ombudsman.
<agent>: Bien sûr, la voie vers l'ombudsman vous est ouverte. Je vous propose que j'escalade le dossier dès aujourd'hui à notre direction sinistres et que nous vous fassions parvenir une prise de position concrète au plus tard après-demain.
<customer>: Bien, faites cela. Mais si je reçois encore une réponse standard, vous ne me reverrez sûrement plus comme cliente.
<agent>: Je prends votre feedback très au sérieux et note votre plainte en détail dans le dossier.
<customer>: D'accord, alors j'attends maintenant UNE dernière fois votre retour.
<agent>: Merci pour votre patience, Madame Roth. Nous vous recontacterons le plus rapidement possible.""",
        "topics": ["4"],
        "summary": "Customer is dissatisfied with compensation after water damage. The case is escalated to claims management, a new review or possible goodwill solution is announced."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Steiner. Ich rufe wegen meines offenen Schadenfalls an. Ich habe seit zwei Wochen nichts mehr gehört.
<agent>: Guten Tag Frau Steiner, hier ist Sarah Dürst von der Vaudoise. Darf ich bitte die Schadenreferenz haben?
<customer>: Ja, das ist SN-2993-Z3.
<agent>: Vielen Dank. Ich schaue kurz nach… Ich sehe, dass wir noch auf eine Rückmeldung der Werkstatt warten, die die Reparaturkosten bestätigen soll.
<customer>: Das kann doch nicht Ihr Ernst sein. Ich habe das Auto vor zehn Tagen zurückbekommen.
<agent>: Es tut mir leid, dass das so lange dauert. Im System ist noch keine finale Rechnung hinterlegt.
<customer>: Ich habe die Rechnung gestern selber per E-Mail geschickt!
<agent>: Einen Moment… ah, ich sehe sie jetzt in unserem Posteingang, aber sie ist noch nicht im Dossier verbucht. Das hätte schneller passieren sollen, da gebe ich Ihnen recht.
<customer>: Ja, genau. Ich kann nicht ständig hinterhertelefonieren.
<agent>: Ich priorisiere Ihren Fall sofort und gebe ihn an die zuständige Schadensachbearbeiterin weiter. Sie erhalten spätestens morgen eine Bestätigung der Auszahlung.
<customer>: Versprechen Sie mir das? Ich habe schon einmal „morgen" gehört.
<agent>: Ich kann Ihnen zusagen, dass ich persönlich einen Reminder setze und Sie morgen Vormittag per E-Mail über den Status informiere.
<customer>: Gut. Wenn ich morgen nichts höre, rufe ich direkt Ihre Vorgesetzte an.
<agent>: Das verstehe ich. Ich kümmere mich darum, dass es gar nicht so weit kommt.
<customer>: Na gut, dann warte ich bis morgen.
<agent>: Vielen Dank, Frau Steiner. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for settlement of a claim. The agent finds an unposted invoice and prioritizes the case, including a personal status update the next day."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller speaking. I have a question about my premiums and payments.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What exactly is it about?
<customer>: I received a reminder yesterday, even though I'm sure I paid.
<agent>: Let's clarify this. Do you have the policy number at hand?
<customer>: Yes, PZ-2519-D4.
<agent>: Thanks. One moment... I see that the premium for the second quarter is still outstanding. Do you perhaps have a payment receipt or the date of the transfer?
<customer>: I paid in the middle of the month. Honestly, this is getting annoying, it's not the first time this happens.
<agent>: I understand that. If you want, you can send me the payment receipt by email, then we'll reconcile the payment with our bookings.
<customer>: Do I have to do this again? Can't you just check the bank?
<agent>: For data protection reasons, we only see our account movements. Without a receipt, it's difficult to search for a specific transfer. However, I can commission an internal reconciliation in parallel.
<customer>: Good, I'll forward you the screenshot from e-banking to keller@gmail.com. Are you using this address?
<agent>: Yes, exactly this one is registered. I'll note that the reminder fee is suspended for now until we've clarified the case.
<customer>: At least that. I definitely don't want to appear as a defaulting payer.
<agent>: That's understandable. As soon as we've found the payment receipt, you'll receive a confirmation and the reminder will be deleted.
<customer>: Okay, then I'll do that right after the phone call.
<agent>: Thank you very much, Mr. Keller. We'll take care of it.""",
        "topics": ["6"],
        "summary": "Customer receives a reminder despite having made payment. The agent suspends the reminder fee and requests payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Alonso. Ich habe einige Fragen zu den Leistungen meiner Gesundheitsunterstützung bei der Vaudoise.
<agent>: Guten Tag Frau Alonso, hier ist Anna Meier. Erzählen Sie mir, worum es konkret geht.
<customer>: Mein Arzt hat mir eine Psychotherapie empfohlen. Ich weiss aber nicht, was genau und wie lange die Vaudoise beteiligt ist.
<agent>: Dafür schauen wir am besten in Ihre Police. Haben Sie Ihre Policennummer zur Hand?
<customer>: Ja, GS-6059-J5.
<agent>: Danke, ich habe Ihre Unterlagen vor mir. Sie haben ein Zusatzpaket mit Beteiligung an ambulanten Therapien.
<customer>: Bedeutet das, dass alles übernommen wird?
<agent>: Nicht ganz. Ich erkläre es Ihnen Schritt für Schritt:
<agent>: Erstens: Es gibt einen Selbstbehalt von 10% auf die Kosten, nachdem die Franchise der Grundversicherung erreicht ist.
<customer>: Okay, und zweitens?
<agent>: Zweitens: Es ist eine maximale Anzahl von 40 Sitzungen pro Jahr vorgesehen, sofern die Therapie ärztlich verordnet und von einer anerkannten Fachperson durchgeführt wird.
<customer>: Und wenn ich mehr als 40 Sitzungen brauche?
<agent>: Drittens: Darüber hinaus gehende Sitzungen können auf Antrag geprüft werden, es gibt aber keine Garantie, dass sie übernommen werden.
<customer>: Verstehe. Viertens?
<agent>: Viertens: Für die erste Kostengutsprache benötigen wir einen Bericht Ihrer behandelnden Ärztin oder Ihres Arztes.
<customer>: Das heisst, ich muss zuerst zum Hausarzt?
<agent>: Genau, fünftens: Der Antrag muss über Ihre Hausärztin oder Ihren Hausarzt laufen. Sie oder er reicht die Unterlagen direkt bei uns ein.
<customer>: Puh, das ist komplizierter als gedacht, aber jetzt habe ich es verstanden.
<agent>: Gerne fasse ich Ihnen alles in einer E-Mail zusammen, damit Sie es in Ruhe nachlesen können. Ist alonso@hotmail.com noch aktuell?
<customer>: Ja, das passt.
<agent>: Wunderbar, dann sende ich Ihnen die Zusammenfassung und ein Merkblatt noch heute.
<customer>: Danke, das hilft mir sehr.
<agent>: Dafür sind wir da, Frau Alonso.""",
        "topics": ["7"],
        "summary": "Customer inquires about coverage for psychotherapy. The agent explains deductible, session count, and application process and sends a written summary."
    },
    {
        "transcript": """<customer>: Hallo, hier ist Herr Keller. Mein Auto ist eben liegengeblieben und ich brauche dringend Pannenhilfe.
<agent>: Guten Tag Herr Keller, hier ist Luca Steiner von der Vaudoise Assistance. Sind Sie und alle Mitfahrenden in Sicherheit?
<customer>: Ja, wir stehen auf einem Parkplatz, aber das Auto springt nicht mehr an.
<agent>: Gut, dann beruhigt mich das schon einmal. Wo genau befinden Sie sich?
<customer>: Auf der A2 Raststätte Richtung Luzern, kurz nach der Ausfahrt Sursee.
<agent>: Danke. Haben Sie Ihre Policennummer oder Ihr Kennzeichen zur Hand?
<customer>: Kennzeichen ist LU 123 456, Policennummer müsste PH-2385-L9 sein.
<agent>: Perfekt, ich sehe, Sie haben das erweiterte Pannenhilfe-Paket. Ich kann sofort einen Abschleppdienst organisieren.
<customer>: Wie lange dauert das ungefähr?
<agent>: Erfahrungsgemäss 30 bis 45 Minuten, je nach Verkehrslage. Der Pannendienst bringt Ihr Fahrzeug zu einer Partnergarage oder auf Wunsch zu Ihrer Stammgarage.
<customer>: In Ordnung. Und was kostet mich das?
<agent>: Der Einsatz selbst ist durch Ihre Pannenhilfe gedeckt. Allfällige Reparaturkosten in der Garage gehen separat.
<customer>: Gut, dann schicken Sie jemanden. Meine Handynummer ist dieselbe wie im System.
<agent>: Ich habe sie hier, der Pannendienst wird Sie kurz vor Ankunft direkt anrufen.
<customer>: Alles klar, danke.
<agent>: Gern geschehen, Herr Keller. Bleiben Sie unbedingt hinter der Leitplanke, falls Sie doch nahe der Autobahn stehen.""",
        "topics": ["8"],
        "summary": "Customer needs immediate roadside assistance on the highway. Assistance organizes a towing service that is covered by the roadside assistance package."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have a question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Marc Ducret from Vaudoise. What's the matter?
<customer>: We bought some new, quite expensive furniture. I'm not sure if the insurance sum is still sufficient.
<agent>: Then let's check that together. Do you have your policy number at hand?
<customer>: Yes, HR-8435-W3.
<agent>: Thanks. Your current insurance sum is 60,000 francs. Do you have an approximate idea of the total value of your household contents after the new purchase?
<customer>: Hard to say, but I think it's rather around 80,000 francs.
<agent>: Then there is indeed a risk of underinsurance. In case of damage, this would mean that compensations could be reduced.
<customer>: I definitely don't want that. But I also don't want to pay unnecessarily high premiums.
<agent>: Understandable. We could offer a free household contents check where you record a list of your largest items online. This results in a realistic insurance sum.
<customer>: Does someone have to come by?
<agent>: No, you can do that conveniently yourself. If you want, I can send you the link to the tool by email and then adjust the policy accordingly.
<customer>: Alright, let's do it that way.
<agent>: Perfect. I'll send you the link to steiner@gmail.com and a proposal for the new insurance sum.
<customer>: Good, then I'll look at that tonight.
<agent>: Thank you very much, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer has significantly upgraded her household contents and fears underinsurance. She receives an online tool to determine an appropriate insurance sum."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich habe Fragen zu meiner Fahrzeugversicherung bei der Vaudoise.
<agent>: Guten Tag Herr Simic, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich hatte einen Steinschlag in der Frontscheibe, und die Werkstatt meint, ich soll das über die Versicherung laufen lassen. Verliere ich dann meinen Bonus?
<agent>: Schauen wir zuerst in Ihre Police. Haben Sie die Nummer zur Hand?
<customer>: Ja, FV-1234-P3.
<agent>: Danke. Sie haben eine Vollkaskoversicherung mit einem speziellen Bonus-Schutz-Modul.
<customer>: Und was heisst das konkret?
<agent>: Das bedeutet, dass ein einzelner Glasschaden Ihren Bonus nicht reduziert. Sie zahlen nur die vereinbarte Selbstbeteiligung, falls überhaupt eine vorgesehen ist.
<customer>: Das klingt schon mal besser. Wie hoch ist die Selbstbeteiligung?
<agent>: Bei Glasschäden ist bei Ihnen keine Selbstbeteiligung hinterlegt.
<customer>: Also zahle ich gar nichts?
<agent>: Die Reparatur der Scheibe wäre in Ihrem Fall vollständig gedeckt, sofern sie bei einer anerkannten Partnerwerkstatt erfolgt.
<customer>: Okay, das ist fair. Können Sie mir eine Liste der Partnerwerkstätten in meiner Nähe per E-Mail senden?
<agent>: Sehr gerne. Ich sende Ihnen eine Übersicht für den Raum Luzern an simic@gmail.com.
<customer>: Super, dann bin ich zufrieden.
<agent>: Freut mich, dass ich helfen konnte, Herr Simic.""",
        "topics": ["10"],
        "summary": "Customer inquires whether glass damage affects his bonus. Thanks to bonus protection and no deductible, the repair is fully covered."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. J'ai une question sur mon assurance voyage.
<agent>: Bonjour Monsieur Berger, ici Marc Ducret de Vaudoise. De quoi s'agit-il?
<customer>: Je pars la semaine prochaine en Thaïlande. Comment cela se passe-t-il si je ne peux pas voyager à cause d'une maladie soudaine?
<agent>: Pour cela, je regarde rapidement dans votre police RV-1208-B3. Vous avez souscrit une assurance frais d'annulation.
<customer>: Et qu'est-ce que cela couvre exactement?
<agent>: Si vous ou une personne co-assurée tombez gravement malades ou avez un accident avant le voyage, nous prenons en charge les frais d'annulation contractuellement dus selon les conditions.
<customer>: Avez-vous alors besoin d'un certificat médical?
<agent>: Oui, une attestation médicale est requise, dont il ressort que le voyage ne peut pas être entrepris d'un point de vue médical.
<customer>: Et si un avertissement de voyage officiel est prononcé?
<agent>: Selon la situation, la couverture est examinée par le biais d'une autre clause, par exemple en cas de force majeure. Nous nous orientons également selon les conseils de voyage de la Confédération.
<customer>: Bien, au moins je ne suis pas complètement livré à moi-même.
<agent>: Exactement, vous avez une protection solide. Si vous voulez, je vous envoie un court mémo sur les points les plus importants.
<customer>: Oui, s'il vous plaît à berger@gmail.com.
<agent>: Je le fais volontiers, Monsieur Berger.""",
        "topics": ["11"],
        "summary": "Customer inquires about cancellation protection in case of illness and travel warnings. The agent explains coverage and requirements, including medical certificate."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Alonso. I have questions about my life insurance with Vaudoise.
<agent>: Good afternoon Mrs. Alonso, this is Sarah Dürst. What would you like to know?
<customer>: My life situation has changed, I now have a child. I'm wondering if the insurance sum is still sensible.
<agent>: Then it's a good time to look at that. Do you have your policy number ready?
<customer>: Yes, LV-4995-Q2.
<agent>: Thanks. Your current insurance sum is 100,000 francs. Do you have an idea of what you'd like as a target sum?
<customer>: Rather 200,000 francs, so that in the worst case at least the mortgage is partially covered.
<agent>: I understand. An increase is basically possible, but a renewed health examination may be required.
<customer>: What exactly does that mean?
<agent>: You would fill out a health questionnaire, and depending on the sum and age, a medical examination could be added.
<customer>: And if something is found?
<agent>: Then there can be reservations or a surcharge. I recommend that we first create a non-binding quote with different variants.
<customer>: Alright. Please send me two variants: one with 150,000 and one with 200,000.
<agent>: Very gladly. I'll send you the quotes to alonso@gmail.com.
<customer>: Thanks, then I'll discuss this with my partner.
<agent>: That's a good idea, Mrs. Alonso.""",
        "topics": ["12"],
        "summary": "Customer has had offspring and wants to increase the insurance sum of her life insurance. A quote with two variants and reference to possible health examination is created."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Wertsachenversicherung.
<agent>: Guten Tag Herr Keller, hier ist Anna Meier von der Vaudoise. Was liegt an?
<customer>: Ich habe eine neue Uhr gekauft, die nicht ganz billig war. Ich möchte wissen, ob die automatisch mitversichert ist.
<agent>: Haben Sie die Policennummer Ihrer Wertsachenversicherung?
<customer>: Ja, WV-6297-D2.
<agent>: Danke. Sie haben eine Pauschaldeckung für Wertsachen bis 20'000 Franken. Wissen Sie ungefähr, wo Sie aktuell mit dem Gesamtwert liegen?
<customer>: Mit der neuen Uhr komme ich wahrscheinlich knapp über 20'000 Franken.
<agent>: Dann wäre es sinnvoll, die Uhr entweder einzeln zu deklarieren oder die Pauschalsumme zu erhöhen.
<customer>: Und was empfehlen Sie?
<agent>: Wenn es sich um ein besonders wertvolles Einzelstück handelt, ist eine Einzeldeklaration vorteilhaft – unter anderem im Schadenfall.
<customer>: In Ordnung. Ich lasse Ihnen die Rechnung und ein Foto zukommen.
<agent>: Perfekt. Senden Sie die Unterlagen bitte an unsere E-Mail-Adresse, die ich Ihnen gleich per Mail zur Bestätigung schicke.
<customer>: Passt, danke.
<agent>: Sehr gerne, Herr Keller.""",
        "topics": ["13"],
        "summary": "Customer wants to insure a new, expensive watch. The agent recommends individual declaration or increasing the lump sum and requests documents."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about my insurance.
<agent>: Good afternoon Mr. Baumann, this is Pascal Tremblay from Vaudoise. What concerns you?
<customer>: I feel like I have too many individual policies and everything is too complicated.
<agent>: I hear that often. We can check a so-called policy bundling.
<customer>: What does that bring me?
<agent>: First: You have fewer documents and a better overview. Second: Often there's a bundling discount. Third: Adjustments can be made more easily.
<customer>: Sounds logical. But I don't want to suddenly be worse insured.
<agent>: I understand that. We would compare your existing coverage point by point:
<agent>: 1. Which risks are covered today?
<agent>: 2. Which coverage could be merged?
<agent>: 3. Where are there duplicate insurances?
<customer>: Duplicate insurances? That would be wasted money.
<agent>: Exactly, and fourth we would check whether the insurance sums still fit your current life situation.
<customer>: And how does that work concretely?
<agent>: I'll send you an overview of your policies in advance by email to baumann@hotmail.com. After that we can arrange a consultation appointment, by phone or on-site.
<customer>: A phone appointment is enough for me first.
<agent>: Good, I'll send you two appointment suggestions for next week right away.
<customer>: Alright, then I'll decide on one of them.
<agent>: Perfect, Mr. Baumann.""",
        "topics": ["1"],
        "summary": "Customer feels overwhelmed by the number of his policies. A bundling with possible discount and structured review of coverage is proposed.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich habe das Gefühl, dass ich bei Ihnen nicht ausreichend versichert bin.
<agent>: Guten Tag Frau Dvorak, hier ist Luca Steiner. Was lässt Sie das vermuten?
<customer>: Eine Freundin hatte einen Brand im Keller, und ein Teil war nicht gedeckt. Jetzt frage ich mich, ob ich auch so eine Lücke habe.
<agent>: Dann prüfen wir das besser. Haben Sie Ihre Policennummer oder Kundennummer zur Hand?
<customer>: UD-3205-U3.
<agent>: Danke. Ich sehe, dass Ihre Hausratversicherung eine relativ tiefe Versicherungssumme ausweist und keine speziellen Zusatzdeckungen für Fahrräder oder Schmuck besitzt.
<customer>: Super. Und das haben Sie mir nicht mal aktiv gesagt.
<agent>: Es tut mir leid, wenn das bisher nicht ausführlich besprochen wurde. Wir können jetzt gemeinsam schauen, was Ihnen wichtig ist.
<customer>: Wichtig ist mir, dass ich im Ernstfall nicht pleite bin.
<agent>: Verstehe. Wir könnten:
<agent>: – die Versicherungssumme erhöhen,
<agent>: – eine spezielle Wertsachendeckung hinzufügen,
<agent>: – und prüfen, ob gewisse Risiken wie Elementarschäden besser abgedeckt werden sollten.
<customer>: Klingt nach höheren Kosten.
<agent>: Es würde die Prämie leicht erhöhen, aber ich kann Ihnen zwei Varianten erstellen: eine Minimalanpassung und eine umfassendere Lösung.
<customer>: Schicken Sie mir beides. Aber ehrlich: Wenn ich das Gefühl habe, dass Sie einfach nur verkaufen wollen, wechsle ich die Versicherung.
<agent>: Ich verstehe Ihre Sorge. Ich werde alles transparent aufschlüsseln, damit Sie selbst entscheiden können.
<customer>: Gut, dann schaue ich mir das an.
<agent>: Vielen Dank, Frau Dvorak.""",
        "topics": ["2"],
        "summary": "Customer suspects gaps in her household contents and valuables coverage. Various adjustment variants with different premium levels are announced.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une demande de vente.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer de Vaudoise. De quoi s'agit-il?
<customer>: Je déménage dans un nouvel appartement, et mon propriétaire exige une assurance responsabilité civile privée et ménage. Mais j'ai actuellement seulement l'assurance auto et voyage.
<agent>: Alors regardons comment nous pouvons compléter cela. Voulez-vous souscrire les deux - ménage et responsabilité civile privée - ensemble?
<customer>: Oui, mais cela ne doit pas être trop cher.
<agent>: Si nous définissons cela comme un paquet, nous pouvons offrir un rabais de combinaison.
<customer>: Pouvez-vous me donner une valeur indicative maintenant?
<agent>: Basé sur votre profil - lieu de résidence, âge et contrats déjà existants - j'estime environ 280 à 320 francs par an pour les deux ensemble.
<customer>: Cela va. Mais j'ai besoin de cela assez urgemment, sinon il y aura des problèmes avec le propriétaire.
<agent>: Nous pourrions créer aujourd'hui une attestation de couverture provisoire. Les documents définitifs, vous les recevrez ensuite par courrier ou email.
<customer>: D'accord. Alors faisons cela.
<agent>: Parfait. Je vous envoie d'abord un bref résumé par email à keller@gmail.com. Dès que vous confirmez, je génère l'attestation de couverture pour votre propriétaire.
<customer>: Faites vite s'il vous plaît, je dois lui donner cela au plus tard demain.
<agent>: Je m'en occupe tout de suite après, Monsieur Keller.""",
        "topics": ["3"],
        "summary": "Customer urgently needs household contents and personal liability insurance for a new apartment. A package with combination discount and provisional coverage certificate is offered."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverhandlung an, und ehrlich gesagt bin ich ziemlich sauer.
<agent>: Guten Tag Frau Dvorak, hier ist Marc Ducret. Es tut mir leid, dass Sie verärgert sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruch bei mir zuhause, Referenz SV-3253-C3. Sie haben diverse Positionen einfach gestrichen.
<agent>: Ich öffne den Fall… Einen Moment bitte… Ja, ich sehe die Korrespondenz. Einige Gegenstände konnten nicht belegt werden.
<customer>: Natürlich habe ich keine Rechnung von einer fünf Jahre alten Tasche mehr. Deswegen war sie ja trotzdem da!
<agent>: Ich verstehe Ihre Sicht. Gemäss Bedingungen sind wir aber auf Nachweise angewiesen, damit wir den Wert einschätzen können.
<customer>: Also glauben Sie mir einfach nicht? Super.
<agent>: Darum geht es nicht. Wir brauchen Anhaltspunkte, zum Beispiel Fotos, Kontoauszüge oder Garantiekarten.
<customer>: Das habe ich schon alles geschickt. Lesen Sie Ihre Mails?
<agent>: Ich sehe, dass gestern tatsächlich noch Fotos nachgereicht wurden, die aber noch nicht im System verknüpft sind. Das hätte schneller gehen müssen, entschuldigen Sie bitte.
<customer>: Ich habe langsam das Gefühl, ich werde hingehalten, damit ich aufgebe.
<agent>: Das ist ganz sicher nicht die Absicht. Ich werde den Fall noch heute an die zuständige Fachperson weitergeben und um eine erneute Prüfung der abgelehnten Positionen bitten.
<customer>: Gut. Wenn sich nichts bewegt, gehe ich damit zur Presse. Das meine ich ernst.
<agent>: Ich nehme Ihre Beschwerde sehr ernst und vermerke sie entsprechend. Sie erhalten bis spätestens Anfang nächster Woche eine schriftliche Stellungnahme.
<customer>: Wir werden sehen.
<agent>: Danke, dass Sie uns trotzdem noch einmal die Chance geben, das zu klären.""",
        "topics": ["4"],
        "summary": "Customer is annoyed about the rejection of burglary claim positions. After submitted photos, a new review is promised and the complaint is noted in the file."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Keller. I'm calling again about my open claim.
<agent>: Good afternoon Mr. Keller, this is Sarah Dürst from Vaudoise. Which claim is it about?
<customer>: Claim No. SN-5073-J8. I was told I would receive a payout last week. So far nothing is there.
<agent>: Let me check... It seems that the payment was released internally, but the bank connection was incomplete.
<customer>: You've had that from me a thousand times already!
<agent>: I see that the IBAN in the system is registered with two digits too few. That's naturally annoying, I'm sorry.
<customer>: That's more than annoying. I'm waiting for the money.
<agent>: Please give me your complete IBAN again so we can correct this.
<customer>: CH12 3456 7890 1234 5678 9.
<agent>: Thanks. I'll correct this immediately and forward the payment for processing again. Additionally, I'll note that any default interest should be checked.
<customer>: At least something. But quite honestly, the trust is pretty much gone by now.
<agent>: I can understand that. I can offer to send you a written confirmation about the renewed triggering this afternoon.
<customer>: Yes, I expect that too.
<agent>: Alright, Mr. Keller. Again, sorry for the circumstances.""",
        "topics": ["5"],
        "summary": "Customer is annoyed waiting for claim payment. Due to incorrect IBAN the payout was delayed, which is now corrected and triggered again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe schon wieder ein Schreiben zu offenen Prämien bekommen.
<agent>: Guten Tag Frau Roth, hier ist Yann Morel von der Vaudoise. Dann schauen wir uns das an. Haben Sie eine Referenznummer?
<customer>: Auf dem Brief steht PZ-6667-O4.
<agent>: Danke. Ich sehe, dass es sich um eine Prämienerhöhung aufgrund einer Vertragsverlängerung handelt. Vielleicht wirkt das wie ein neuer offener Betrag.
<customer>: Aber es ist deutlich mehr als letztes Jahr. Das kann doch nicht sein.
<agent>: Die Prämie wurde aufgrund höherer Schadenbelastung in Ihrem Segment angepasst. Zusätzlich ist eine Indexierung eingeflossen.
<customer>: Das heisst auf gut Deutsch: Ich zahle mehr, ohne dass ich etwas dafür bekomme.
<agent>: Die Deckung bleibt zwar gleich, aber die Kosten im Hintergrund steigen. Auf Wunsch könnten wir Deckungen anpassen, um die Prämie zu reduzieren.
<customer>: Zum Beispiel?
<agent>: Man könnte die Selbstbeteiligung leicht erhöhen oder einzelne optionale Zusatzbausteine streichen.
<customer>: Und wenn ich das nicht will?
<agent>: Dann bleibt die Prämie wie im Schreiben angegeben. Selbstverständlich steht es Ihnen frei, den Markt zu vergleichen.
<customer>: Vielleicht mache ich das. Im Moment bin ich wirklich nicht begeistert.
<agent>: Das verstehe ich. Wenn Sie möchten, kann ich Ihnen mindestens ein oder zwei Sparvarianten ausrechnen und per E-Mail senden.
<customer>: Schicken Sie es an roth@gmail.com. Aber ohne Schönrederei.
<agent>: Ich sende Ihnen eine nüchterne Aufstellung, versprochen.""",
        "topics": ["6"],
        "summary": "Customer is annoyed about a significant premium increase. The agent explains reasons and offers savings variants through coverage adjustment."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Roth. J'ai des questions de santé en relation avec ma police.
<agent>: Bonjour Madame Roth, ici Pascal Tremblay. En quoi puis-je vous aider?
<customer>: J'ai été inscrite pour une réhabilitation, et la clinique veut savoir ce que Vaudoise prend exactement en charge.
<agent>: Alors regardons dans votre police GS-1199-B4. Vous avez un paquet de réha avec une durée limitée.
<customer>: Combien de temps exactement?
<agent>: En principe, 21 jours de réha stationnaire par an sont couverts, pour autant qu'elle soit médicalement indiquée et approuvée au préalable.
<customer>: Mon médecin a dit que j'ai besoin d'au moins quatre semaines.
<agent>: Les jours supplémentaires pourraient passer par l'assurance de base ou un examen de cas individuel. Nous avons besoin pour cela d'un rapport détaillé de votre médecin.
<customer>: Et si cela est refusé?
<agent>: Alors les coûts supplémentaires seraient en partie ou entièrement à votre charge. Je recommande que nous demandions d'abord l'autorisation de coûts pour les 21 jours et examinions la prolongation en parallèle.
<customer>: D'accord, envoyez-moi une liste de ce que mon médecin doit soumettre.
<agent>: Très volontiers, je vous envoie un mémo à roth@gmail.com.
<customer>: Merci. J'espère que cela fonctionne sans paperasserie interminable.
<agent>: Nous essayons de garder le processus aussi simple que possible.""",
        "topics": ["7"],
        "summary": "Customer needs clarity about rehabilitation benefits. 21 days of rehabilitation are covered, an extension will be reviewed based on medical report."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich rufe wegen meiner Pannenhilfe an – beziehungsweise wegen deren Grenzen.
<agent>: Guten Tag Frau Roth, hier ist Nora Widmer von der Vaudoise. Was ist passiert?
<customer>: Gestern Nacht ist mein Auto in Deutschland stehen geblieben, und mir wurde gesagt, das sei nicht gedeckt.
<agent>: Ich schaue in Ihre Police PH-5104-L8… Sie haben eine Pannenhilfe, die standardmässig auf die Schweiz und das Fürstentum Liechtenstein beschränkt ist.
<customer>: Ja, das hat mir der Herr am Telefon dann auch gesagt – aber ganz ehrlich, das hätte man mir früher sagen müssen.
<agent>: Ich verstehe Ihren Ärger. Für Fahrten ins Ausland empfehlen wir ein erweitertes Assistance-Paket.
<customer>: Ja, jetzt weiss ich das auch. Bringt mir nur nichts mehr, das Taxi und der Rücktransport haben mich ein Vermögen gekostet.
<agent>: Für diesen konkreten Fall können wir leider nichts mehr rückwirkend decken. Was ich tun kann, ist Ihnen ein Angebot für die Zukunft zu machen.
<customer>: Das ist wenig tröstlich. Ich überlege mir ernsthaft, die Versicherung zu wechseln.
<agent>: Das tut mir sehr leid zu hören. Ich würde dennoch gerne sicherstellen, dass Sie künftig besser geschützt sind – ob bei uns oder anderswo. Darf ich Ihnen eine Übersicht über die möglichen Ausland-Assistance-Varianten schicken?
<customer>: Meinetwegen. Aber ehrlich, ich bin enttäuscht.
<agent>: Das kann ich nachvollziehen. Ich sende Ihnen die Übersicht an roth@gmail.com.
<customer>: Tun Sie das. Ich entscheide dann, ob ich bleibe.
<agent>: Danke, dass Sie uns trotzdem noch eine Chance geben, Frau Roth.""",
        "topics": ["8"],
        "summary": "Customer had a breakdown abroad that wasn't covered and is disappointed. The agent explains coverage limits and offers future foreign assistance options."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I have another question about my property insurance.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner from Vaudoise. What can I do for you?
<customer>: After the last phone call, I looked at your documents and found that my basement isn't specifically mentioned.
<agent>: Basement compartments are usually co-insured as long as they're at the same location. Let me quickly check your policy HR-1056-J5.
<customer>: But my basement is in the neighboring house. Does that count too?
<agent>: That's an important difference. If it's in another building, it might need a special agreement.
<customer>: And why doesn't anyone tell me this when I take out the policy?
<agent>: That could have been communicated more clearly, you're right there. But we can catch up on this now and explicitly include your basement in the policy.
<customer>: What does that cost me?
<agent>: That depends on the value of the stored items. If you give me a rough estimate, I can create a quote.
<customer>: Let's say 8,000 francs.
<agent>: Alright. I'll create a quote for you and send it to steiner@gmail.com. Only when you agree in writing will the coverage be extended.
<customer>: Good. This time I'll read everything very carefully.
<agent>: That's very sensible, Mrs. Steiner.""",
        "topics": ["9"],
        "summary": "Customer discovers that her external basement compartment isn't clearly mentioned. A special agreement with quote for co-insurance is proposed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Es geht um meine Fahrzeugversicherung.
<agent>: Guten Tag Frau Dvorak, hier ist Sarah Dürst. Worum geht es genau?
<customer>: Ich habe einen Brief bekommen, dass meine Kaskoversicherung wegen ausstehender Zahlung gesperrt wurde. Ich bin aber sicher, dass ich bezahlt habe.
<agent>: Lassen Sie mich Ihre Police FV-5163-G4 öffnen. Ich sehe hier tatsächlich eine temporäre Sistierung.
<customer>: Was heisst das konkret? Wenn ich jetzt einen Unfall habe, bin ich nicht versichert?
<agent>: Die Haftpflichtdeckung bleibt bestehen, aber Kaskoschäden wären momentan nicht gedeckt.
<customer>: Das ist ja wohl ein Witz. Ich habe vor zwei Wochen überwiesen.
<agent>: Es tut mir sehr leid. Wenn Sie möchten, können wir zusammen nachsehen, ob wir die Zahlung bereits erhalten haben und sie nur noch nicht zugeordnet wurde.
<customer>: Ich habe gerade keinen Beleg zur Hand, aber ich kann Ihnen später einen Screenshot schicken.
<agent>: Das wäre hilfreich. Alternativ könnten Sie den Betrag heute nochmals überweisen und wir würden bei Doppelzahlung umgehend zurückerstatten.
<customer>: Sicher nicht. Ich zahle nicht doppelt.
<agent>: Das verstehe ich. Dann warten wir auf Ihren Screenshot, setzen die Sistierung aber schon heute zur Überprüfung auf Priorität.
<customer>: Machen Sie das. Und bitte informieren Sie mich schriftlich, sobald alles wieder aktiv ist.
<agent>: Selbstverständlich, Frau Dvorak.""",
        "topics": ["10"],
        "summary": "Customer is annoyed about suspension of comprehensive coverage due to allegedly outstanding premium. She doesn't want to pay double amount and sends payment receipt for clarification."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Baumann. I have a question about my travel insurance.
<agent>: Hello Mr. Baumann, this is Anna Meier from Vaudoise. What's it about?
<customer>: My flight was cancelled by the airline, and I was told I need to handle this through my insurance.
<agent>: Let me check your policy RV-7970-V7. Basically, in case of flight cancellations, the airline is primarily responsible.
<customer>: Yes, but they're currently pushing it to "force majeure" and only want to give me a voucher.
<agent>: In such cases, your travel insurance can partially help, for example with additional costs for hotel or replacement flight, depending on the cause.
<customer>: It was a strike. Does that count?
<agent>: Strikes are covered to a limited extent in many policies. I see that your contract provides certain benefits, but only under certain conditions.
<customer>: Quite honestly, I feel like I'm being pushed around between airline and insurance.
<agent>: I can understand that well. What I can do: Send us the written statement from the airline, and we'll check specifically which positions we can cover.
<customer>: Good, then I'll do that. But I expect a clear answer, not just paragraphs.
<agent>: I'll explicitly note this hint in the file so that the answer is formulated as understandably as possible.""",
        "topics": ["11"],
        "summary": "Customer is caught between airline and insurance after flight cancellation. The agent requests documents to check travel insurance coverage for strikes."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer von der Vaudoise. Wie kann ich helfen?
<customer>: Ich überlege mir, die Police ganz zu kündigen. Ich zahle schon so viel und habe das Gefühl, ich brauche das nicht.
<agent>: Dann sollten wir gemeinsam anschauen, was die Konsequenzen wären. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-5949-B6.
<agent>: Danke. Bei einer Kündigung jetzt würden Sie einen Rückkaufswert erhalten, der unter der bisher einbezahlten Summe liegt.
<customer>: Das klingt nicht gerade attraktiv.
<agent>: Nein, kurzfristig ist der Rückkaufswert oft tiefer. Langfristig bietet die Police einen Todesfallschutz und teilweise auch Sparkomponenten.
<customer>: Ich weiss, aber das Geld fehlt mir im Alltag.
<agent>: Eine Alternative wäre, die Prämie zu reduzieren oder den Vertrag für eine gewisse Zeit prämienfrei zu stellen, anstatt ihn ganz zu beenden.
<customer>: Heisst das, ich würde vorübergehend nichts mehr zahlen?
<agent>: Genau. Die Leistungen würden entsprechend reduziert, aber der Vertrag bliebe bestehen.
<customer>: Schicken Sie mir bitte beide Varianten: Kündigung mit Rückkaufswert und Prämienreduktion.
<agent>: Sehr gerne, ich sende Ihnen eine Übersicht an baumann@hotmail.com.
<customer>: Dann entscheide ich danach.
<agent>: Das klingt gut, Herr Baumann.""",
        "topics": ["12"],
        "summary": "Customer thinks about cancelling life insurance. Alternatives like premium reduction or premium-free continuation are shown."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Keller. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Monsieur Keller, ici Nora Widmer. Que voulez-vous savoir?
<customer>: J'ai acheté des bijoux à l'étranger. Sont-ils déjà assurés sur le chemin du retour ou seulement quand ils sont à la maison?
<agent>: Un bon point. Dans votre police WV-3507-W9, les objets de valeur sont assurés mondialement contre le vol, pour autant que certaines prescriptions de sécurité soient respectées.
<customer>: Quelles prescriptions?
<agent>: Par exemple, vous ne devez pas laisser les bijoux sans surveillance dans la voiture, et à l'hôtel vous devez utiliser le coffre-fort, s'il y en a un.
<customer>: Et si quelqu'un m'arrache le sac dans la rue?
<agent>: S'il s'agit d'un vol, ce serait en règle générale couvert, tant que vous n'avez pas agi avec négligence grave.
<customer>: D'accord, cela me rassure un peu. Alors j'espère que rien n'arrive du tout.
<agent>: Nous l'espérons aussi. Si vous voulez, vous pouvez nous envoyer après le retour une copie des justificatifs d'achat, pour que les valeurs soient actualisées dans le système.
<customer>: Je le fais.
<agent>: Parfait, Monsieur Keller.""",
        "topics": ["13"],
        "summary": "Customer asks about worldwide coverage of his newly acquired jewelry. The agent explains conditions and recommends submitting purchase receipts for updating."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. Another general question about Vaudoise.
<agent>: Good afternoon Mrs. Steiner, this is Pascal Tremblay. What's it about?
<customer>: I'm considering bundling all my insurance with a single provider. Before I do this with you, I want to know if I really only have one contact person in case of damage.
<agent>: A justified question. With us you receive a main contact who coordinates your files, even when various specialist departments are involved.
<customer>: Does that mean I don't have to tell everything multiple times?
<agent>: Exactly. Your main contact has access to relevant information and can internally involve the right places.
<customer>: Good, because this constant repetition annoys me with other providers.
<agent>: If you want, we can arrange a personal appointment where we go through your existing insurance and make a bundling offer.
<customer>: Send me a rough overview first before I invest time in an appointment.
<agent>: Of course, I'll send you an initial rough concept to steiner@gmail.com.
<customer>: Good, then we'll see further.
<agent>: Very gladly, Mrs. Steiner.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance with Vaudoise and asks about a central contact person. A rough concept is promised by email."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Simic. Je crains de ne pas avoir assuré certaines choses qui me sont importantes.
<agent>: Bonjour Monsieur Simic, ici Pascal Tremblay de Vaudoise. Quelles choses voulez-vous dire concrètement?
<customer>: Je travaille parfois depuis la maison et j'ai un équipement informatique coûteux dans le home office. Cela n'est mentionné nulle part explicitement.
<agent>: Je regarde dans vos documents avec la référence UD-2064-E3. Votre assurance ménage couvre en principe aussi les appareils de travail, mais seulement jusqu'à un certain montant.
<customer>: Et si la valeur est au-dessus?
<agent>: Alors nous aurions effectivement une lacune. Dans de nombreux cas, cela peut être comblé avec un module supplémentaire ou une solution d'affaires spéciale.
<customer>: Je ne veux pas soudainement entendre que c'est ma faute si on cambriole.
<agent>: C'est compréhensible. Je propose que nous saisissions la valeur approximative de votre équipement et que je calcule une couverture supplémentaire appropriée.
<customer>: Faites cela. Si c'est complètement excessif, je me cherche une autre solution.
<agent>: J'essaie de créer une offre équitable et transparente. Vous la recevrez à simic@gmail.com.
<customer>: D'accord.
<agent>: Merci, Monsieur Simic.""",
        "topics": ["2"],
        "summary": "Customer is unsure whether his home office equipment is sufficiently insured. The agent checks household contents coverage and creates an additional quote."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Simic. Ich wurde von einem Kollegen auf eine Kombi-Lösung bei der Vaudoise aufmerksam gemacht.
<agent>: Guten Tag Herr Simic, hier ist Marc Ducret. Meint Ihr Kollege vielleicht ein Paket aus Auto-, Hausrat- und Privathaftpflichtversicherung?
<customer>: Genau. Ich habe bisher nur die Fahrzeugversicherung bei Ihnen.
<agent>: Dann könnte sich ein Wechsel der anderen Versicherungen zu uns tatsächlich lohnen. Wir bieten bei Paketlösungen Rabatte an.
<customer>: Aber ich will keine Hochglanzverkaufsshow, nur klare Zahlen.
<agent>: Verstehe ich gut. Ich kann Ihnen auf Basis Ihrer aktuellen Situation eine nüchterne Vergleichsrechnung machen.
<customer>: Gut. Wenn sich nichts wirklich ändert, bleibe ich, wie ich bin.
<agent>: Das ist fair. Ich sende Ihnen eine Gegenüberstellung „Heute vs. Paketlösung" an simic@gmail.com.
<customer>: In Ordnung.
<agent>: Vielen Dank, dass Sie eine Paketlösung überhaupt in Betracht ziehen, Herr Simic.""",
        "topics": ["3"],
        "summary": "Customer is interested in a package solution with discounts but wants a clear numerical basis. A comparison calculation is created.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Steiner. I'm calling again about my claim negotiation - I'm getting fed up.
<agent>: Good afternoon Mrs. Steiner, this is Luca Steiner. I remember your case SV-6926-G8. What's currently the problem?
<customer>: I was promised on the phone that the deductible would be reduced, and now the original amount is in the letter again.
<agent>: Let me look at the notes... Indeed, it says here that a reduction was put in prospect, but apparently wasn't definitively approved yet.
<customer>: For me it came across like a commitment. I feel fooled.
<agent>: That was unfortunately formulated, I admit. I can now discuss the case directly with claims management.
<customer>: I expect you to keep your word - even if it was only "put in prospect".
<agent>: I understand your position. Can we do it like this: I'll get back to you by tomorrow with a final decision. Should the reduction be rejected, you'll receive a written justification.
<customer>: And if they write unclearly again, like before?
<agent>: I'll ask that the formulation be particularly understandable. And if you want, I'll additionally call you to explain everything personally.
<customer>: Alright. But this is your last chance, otherwise I'm gone.
<agent>: I take that very seriously, Mrs. Steiner.""",
        "topics": ["4"],
        "summary": "Customer is annoyed because a promised deductible reduction wasn't implemented in the letter. The case is clarified directly with claims management."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Schaden-Nachverfolgung.
<agent>: Guten Tag Herr Keller, hier ist Sarah Dürst. Um welchen Schaden geht es?
<customer>: SN-5675-E1, der Sturmschaden an meinem Dach. Ich weiss nicht, ob der Kostenvoranschlag akzeptiert wurde.
<agent>: Ich schaue… Ja, der Kostenvoranschlag der Firma wurde heute Morgen genehmigt.
<customer>: Aha, davon weiss ich nichts.
<agent>: Es hätte eine automatische E-Mail ausgelöst werden sollen. Offenbar hat das noch nicht geklappt.
<customer>: Das wundert mich nicht. Ich habe ohnehin das Gefühl, immer hinterherlaufen zu müssen.
<agent>: Es tut mir leid, dass dieser Eindruck entsteht. Ich sende Ihnen die Bestätigung gleich manuell zu.
<customer>: Gut. Und wann sehe ich das Geld?
<agent>: Die Auszahlung erfolgt nach Einreichen der Schlussrechnung. Bis dahin können Sie mit der Reparatur starten.
<customer>: Na gut, dann mache ich das so.
<agent>: Danke für Ihr Verständnis, Herr Keller.""",
        "topics": ["5"],
        "summary": "Customer waits for feedback on storm damage. The cost estimate is already approved, but the automatic notification didn't work; it's now sent manually."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Keller. I have a question about a premium invoice.
<agent>: Hello Mr. Keller, this is Anna Meier from Vaudoise. What's wrong with the invoice?
<customer>: Suddenly an annual payment is debited instead of a semi-annual one. I didn't change anything.
<agent>: Let me check your policy PZ-2949-B2. Here I see a changeover per contract renewal, where it was switched to annual payment by default.
<customer>: Without me signing anything?
<agent>: There was information in the renewal letter. If you don't agree with this, we can go back to semi-annual payment method.
<customer>: Yes, please. I can't just pay the whole amount at once.
<agent>: No problem. I'll reset the payment method, and the currently due invoice will be adjusted accordingly.
<customer>: Good. And please highlight such things more clearly next time.
<agent>: I'll gladly pass on your feedback, Mr. Keller.""",
        "topics": ["6"],
        "summary": "Customer notices a switch from semi-annual to annual payment method without his active involvement. The payment method is adjusted again."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Berger. Ich wollte mich nach einer Unterstützung im Bereich Gesundheit erkundigen.
<agent>: Guten Tag Herr Berger, hier ist Yann Morel. Was genau interessiert Sie?
<customer>: Ich würde gerne an einem Präventionskurs für Rückentraining teilnehmen. Wird das teilweise übernommen?
<agent>: In Ihrer Police GS-8082-V9 gibt es ein Präventionsbudget, das für anerkannte Kurse genutzt werden kann.
<customer>: Wie hoch ist dieses Budget?
<agent>: Pro Jahr stehen Ihnen 300 Franken zur Verfügung, wenn der Kurs gewisse Kriterien erfüllt.
<customer>: Was für Kriterien?
<agent>: Der Anbieter muss zertifiziert sein, und der Kurs muss ein definiertes Programm umfassen, zum Beispiel über acht bis zehn Wochen.
<customer>: Okay, dann frage ich beim Kursanbieter nach einer Bestätigung.
<agent>: Genau, und schicken Sie uns danach die Kursbestätigung und Zahlungsbelege.
<customer>: Gut, dann mache ich das so.
<agent>: Perfekt, Herr Berger. So können Sie etwas für Ihren Rücken tun und gleichzeitig von der Versicherung profitieren.""",
        "topics": ["7"],
        "summary": "Customer inquires about prevention services for a back course. There is an annual prevention budget if course and provider meet certain criteria."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Berger. Je voulais encore savoir quelque chose sur l'assistance panne.
<agent>: Bonjour Monsieur Berger, ici Yann Morel. Volontiers, que voulez-vous savoir?
<customer>: L'assistance panne vaut-elle aussi pour la voiture de ma partenaire si je conduis?
<agent>: Je regarde dans votre police PH-1780-E5. Dans votre cas, l'assistance panne est liée au véhicule, pas à la personne.
<customer>: Cela signifie que si je conduis avec sa voiture, je n'ai pas de chance?
<agent>: Pour cette voiture, votre assistance panne ne serait effectivement pas valable. Il faudrait une couverture propre ou une solution basée sur la personne.
<customer>: Eh bien, bravo. C'est sûrement écrit tout petit quelque part dans le texte, ou?
<agent>: C'est dans les conditions, oui, mais je comprends qu'on puisse facilement passer à côté.
<customer>: Franchement, cela m'énerve passablement.
<agent>: Je peux le comprendre. Si votre partenaire veut, nous pouvons examiner si une option assistance panne pour son véhicule ou une assistance basée sur les personnes en vaut la peine.
<customer>: Envoyez-moi d'abord des infos avant que je signe encore quelque chose.
<agent>: Très volontiers, je vous envoie un aperçu avec les deux possibilités à berger@gmail.com.""",
        "topics": ["8"],
        "summary": "Customer learns that his roadside assistance is vehicle-related and doesn't apply to his partner's car. He receives information about possible additional solutions."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I'm calling about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. How can I help?
<customer>: I've gone through your long policy and am honestly completely overwhelmed by the technical terms.
<agent>: Many people feel that way. Are there specific points that are unclear to you?
<customer>: For example, what exactly "new value compensation" means.
<agent>: That means that in case of damage we basically replace the replacement value of an equivalent new item, not just the time value.
<customer>: That at least sounds good. And what about things that are no longer manufactured?
<agent>: Then a comparable product or the monetary value is replaced.
<customer>: Could you perhaps send me a simplified summary of the most important points?
<agent>: Very gladly, I can create a simplified coverage sheet for you and send it to dvorak@hotmail.com.
<customer>: That would be great, then I finally understand what I actually bought.
<agent>: Very gladly, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is overwhelmed by technical terms in the property policy. The agent explains new value compensation and sends a simplified summary."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Worum geht es?
<customer>: Ich möchte wissen, ob sich ein Wechsel von Vollkasko auf Teilkasko lohnt. Mein Auto ist schon älter.
<agent>: Wie alt ist das Fahrzeug?
<customer>: Acht Jahre.
<agent>: Oft lohnt sich ab einem gewissen Fahrzeugalter tatsächlich ein Wechsel. Ich sehe in Ihrer Police FV-6623-H3, dass der Zeitwert schon deutlich gesunken ist.
<customer>: Und was spare ich ungefähr?
<agent>: Grob geschätzt könnten Sie rund 25 bis 30 Prozent der Prämie sparen.
<customer>: Und was verliere ich dafür?
<agent>: Sie wären bei selbstverschuldeten Kollisionen nicht mehr gedeckt, nur noch bei Ereignissen wie Diebstahl, Brand, Glasbruch, Elementarschäden und so weiter.
<customer>: Hm, ich denke, das Risiko kann ich eingehen.
<agent>: Wenn Sie möchten, kann ich eine Offerte für die Umstellung erstellen. Sie müssen diese dann nur noch bestätigen.
<customer>: Ja, schicken Sie sie mir.
<agent>: Gerne an keller@gmail.com.
<customer>: Genau.
<agent>: Dann mache ich das gleich, Herr Keller.""",
        "topics": ["10"],
        "summary": "Customer checks switching from comprehensive to partial coverage for an older vehicle. He receives a quote with premium savings and changed coverage."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Ich habe Fragen zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Was möchten Sie wissen?
<customer>: Ich plane eine Weltreise über mehrere Monate. Deckt meine aktuelle Police das überhaupt ab?
<agent>: Ich sehe mir Ihre Police RV-8954-C5 an. Sie ist primär für einzelne Reisen bis maximal 90 Tage ausgelegt.
<customer>: Meine Reise dauert aber mindestens sechs Monate.
<agent>: Dann reicht die aktuelle Police nicht aus. Wir müssten eine spezielle Langzeit-Reiselösung prüfen.
<customer>: Und warum steht das nicht klar irgendwo drauf?
<agent>: Es steht in den Bedingungen, aber ich gebe Ihnen recht, für längere Reisen ist das nicht sofort ersichtlich.
<customer>: Ganz ehrlich, das hätte ich fast übersehen. Ich wäre monatelang unterwegs gewesen und hätte gedacht, ich sei versichert.
<agent>: Gut, dass Sie vorher nachfragen. Ich kann Ihnen eine Offerte für eine Langzeitlösung erstellen oder, falls gewünscht, andere Optionen mit Ihnen besprechen.
<customer>: Schicken Sie mir eine Offerte, alles weitere sehe ich dann.
<agent>: Gerne, an roth@gmail.com.
<customer>: Ja, genau.
<agent>: Vielen Dank, Frau Roth.""",
        "topics": ["11"],
        "summary": "Customer plans a multi-month world trip. Her standard travel insurance only covers trips up to 90 days, so a long-term solution is created as a quote."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baumann. I have a general question about Vaudoise.
<agent>: Good afternoon Mr. Baumann, this is Yann Morel. How can I help you?
<customer>: I'm wondering if I still need my existing insurance at all or if I'm over-insured.
<agent>: A justified question. We can do a so-called needs analysis.
<customer>: And does that mean you then want to sell me even more?
<agent>: Not necessarily. The goal is to find out what really fits your situation - that can also mean reducing something.
<customer>: That would be important to me.
<agent>: If you want, I'll send you a short questionnaire about household, income, family and assets. On this basis we can then review your coverage.
<customer>: Send it to baumann@gmail.com, but without marketing phrases.
<agent>: Understood, Mr. Baumann. I'll stick to the facts.""",
        "topics": ["1"],
        "summary": "Customer fears over-insurance. The agent offers a needs analysis via questionnaire where reductions are also possible.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Roth. I have another question about unmet insurance needs.
<agent>: Good afternoon Mrs. Roth, this is Sarah Dürst. What specifically is it about?
<customer>: I have a dog and I'm wondering if I need special liability insurance for that.
<agent>: In your personal liability insurance, pets are partially co-covered, depending on type and use. Let me quickly check this based on your file UD-4270-U4.
<customer>: He's a normal family dog, not a listed breed or anything.
<agent>: Then he would basically be co-insured, although there are maximum amounts and exclusions.
<customer>: And if he bites someone?
<agent>: Such damage would normally be covered, provided you meet the duty of care.
<customer>: Okay, that reassures me. So I don't need an extra policy?
<agent>: Not necessarily in your case. However, there are special animal owner policies with extended benefits if you want that.
<customer>: No, if it's sufficient like this, let's leave it at that.
<agent>: Alright, then there's no additional need in this area.""",
        "topics": ["2"],
        "summary": "Customer asks if her dog is sufficiently covered by personal liability insurance. There is basic coverage, so no additional policy is necessarily needed."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Steiner. J'ai une demande de vente.
<agent>: Bonjour Madame Steiner, ici Yann Morel. Qu'est-ce qui vous intéresse?
<customer>: J'ai pensé à souscrire une petite assurance vie pour la sécurité de mes enfants.
<agent>: C'est un sujet sensé. Avez-vous déjà une idée de la somme d'assurance souhaitée?
<customer>: Peut-être 50'000 francs par enfant.
<agent>: Nous pourrions établir une police avec une durée fixe jusqu'à un certain âge de vos enfants.
<customer>: Et qu'est-ce que cela me coûterait approximativement?
<agent>: Cela dépend de votre âge et de votre état de santé. En gros, nous sommes à quelques centaines de francs par an.
<customer>: Envoyez-moi s'il vous plaît une offre concrète. Je ne veux décider qu'une fois que j'ai vu les chiffres.
<agent>: Très volontiers, je vous envoie une offre avec deux variantes à steiner@gmail.com.
<customer>: Bien, alors je réfléchis à cela.
<agent>: Parfait, Madame Steiner.""",
        "topics": ["3"],
        "summary": "Customer is interested in a small life insurance for securing her children. She receives a quote with various variants."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Dvorak. Ich rufe wegen meiner Schadenverfolgung an – schon wieder.
<agent>: Guten Tag Frau Dvorak, hier ist Anna Meier. Es tut mir leid, dass Sie erneut anrufen müssen. Um welchen Schaden geht es?
<customer>: Um den Wasserschaden von letzter Woche, SN-4974-L3. Mir wurde ein Rückruf versprochen, aber niemand hat sich gemeldet.
<agent>: Ich sehe im System tatsächlich einen offenen Rückrufauftrag, der noch nicht erledigt wurde. Das hätte nicht passieren dürfen.
<customer>: So langsam glaube ich Ihnen gar nichts mehr.
<agent>: Ich verstehe Ihren Frust und entschuldige mich dafür. Ich kann Ihnen jetzt direkt Auskunft geben, wenn Sie möchten.
<customer>: Ja, bitte.
<agent>: Die Offerte des Handwerkers wurde genehmigt, Sie können mit der Reparatur beginnen. Die Zahlung erfolgt nach Eingang der Schlussrechnung.
<customer>: Warum sagt mir das niemand einfach rechtzeitig?
<agent>: Wir müssen unsere internen Abläufe verbessern, das ist offensichtlich. Ich werde den Vorgang als Beschwerde markieren.
<customer>: Tun Sie das. Vielleicht ändert sich dann etwas.
<agent>: Ich hoffe es auch, Frau Dvorak.""",
        "topics": ["5"],
        "summary": "Customer is annoyed because promised callbacks were missed. The approved claim is explained and the process is noted as a complaint."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Alonso. J'ai une question sur mes primes.
<agent>: Bonjour Madame Alonso, ici Marc Ducret. Que voulez-vous savoir?
<customer>: J'ai vu que j'ai un rabais pour plusieurs produits. Si j'annule une police, est-ce que je perds le rabais sur toutes les autres?
<agent>: Je vérifie votre police PZ-1231-V4. Votre rabais multiple dépend de trois produits de base: ménage, responsabilité civile et assurance véhicule.
<customer>: Et si je change l'assurance véhicule chez un autre fournisseur?
<agent>: Alors le rabais multiple serait réduit ou supprimé, ce qui peut conduire à des primes plus élevées sur les polices restantes.
<customer>: Donc à la fin, je ne fais peut-être aucun gain si je ne change qu'un contrat?
<agent>: Exactement, c'est pourquoi il vaut la peine de considérer l'effet global.
<customer>: Envoyez-moi s'il vous plaît une comparaison "avec assurance véhicule chez vous" et "sans".
<agent>: Très volontiers, je vous envoie cette comparaison à alonso@gmail.com.
<customer>: Alors je calcule tranquillement.
<agent>: C'est une très bonne idée, Madame Alonso.""",
        "topics": ["6"],
        "summary": "Customer wants to know how cancelling vehicle insurance affects her multiple discount. She receives a comparison of total premiums."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Baumann. Ich habe eine Frage zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Baumann, hier ist Nora Widmer. Worum geht es?
<customer>: Mein Zahnarzt hat mir eine Zahnreinigung empfohlen, die ziemlich teuer ist. Zahlt die Vaudoise etwas daran?
<agent>: In Ihrer Police GS-9392-W8 ist eine Beteiligung an Dentalhygiene-Leistungen bis zu einem jährlichen Höchstbetrag vorgesehen.
<customer>: Wie hoch ist der?
<agent>: Maximal 150 Franken pro Jahr.
<customer>: Das ist besser als nichts. Muss die Dentalhygienikerin speziell anerkannt sein?
<agent>: Ja, sie sollte bei einem anerkannten Berufsverband registriert sein. Das steht normalerweise auf der Rechnung.
<customer>: Gut, dann achte ich darauf.
<agent>: Reichen Sie uns die Rechnung einfach ein, und wir prüfen die Beteiligung.
<customer>: Alles klar, danke.
<agent>: Sehr gern, Herr Baumann.""",
        "topics": ["7"],
        "summary": "Customer asks about insurance contribution to professional teeth cleaning. There is an annual contribution provided the provider is recognized."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Berger. I want to ask a question about my roadside assistance.
<agent>: Hello Mr. Berger, this is Yann Morel. How can I help?
<customer>: If I'm traveling with a rental car, am I covered by my roadside assistance?
<agent>: In your policy PH-1780-E5, the coverage refers to your own vehicle with the registered license plate.
<customer>: So no?
<agent>: Exactly, your roadside assistance doesn't apply to a rental car. Most rental car providers have their own assistance services.
<customer>: Good to know. Then I need to look more carefully there.
<agent>: That's definitely recommended.
<customer>: Thanks for the clear answer.
<agent>: Very gladly, Mr. Berger.""",
        "topics": ["8"],
        "summary": "Customer inquires whether his roadside assistance also applies to rental cars. The coverage is vehicle-related and doesn't apply to rental vehicles."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Dvorak. I have a longer question about my property insurance.
<agent>: Good afternoon Mrs. Dvorak, this is Anna Meier. Tell me what concerns you.
<customer>: I recently renovated quite a bit and bought new appliances. I'm afraid I've overlooked something important.
<agent>: Then let's go through this systematically. Your policy HR-7227-U5 is currently issued for 70,000 francs household contents.
<customer>: That was before the renovations.
<agent>: Exactly. We could check it in five steps:
<agent>: First: We roughly record the value of your new furniture and appliances.
<customer>: That's certainly 15,000 to 20,000 francs.
<agent>: Second: We look at whether there are special individual pieces like designer items or antiques that should be listed separately.
<customer>: An antique table would be there.
<agent>: Third: We check whether the location of your risk has changed, for example through a move or major structural changes.
<customer>: No, the apartment is the same.
<agent>: Fourth: We calculate an adjusted insurance sum so you're not underinsured.
<customer>: And fifth?
<agent>: Fifth: We decide together whether additional modules like extended elemental damage or glass breakage make sense.
<customer>: Good, that sounds like a plan. Can you summarize this in writing for me?
<agent>: Very gladly, I'll send you a summary and a proposal for the new insurance sum to dvorak@hotmail.com.
<customer>: Thanks, then I'll go through everything in peace.
<agent>: Perfect, Mrs. Dvorak.""",
        "topics": ["9"],
        "summary": "Customer is concerned about underinsurance after renovations and new purchases. A structured 5-point plan for adjusting property insurance is agreed upon.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Keller. Ich habe nochmals eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Herr Keller, hier ist Marc Ducret. Was möchten Sie wissen?
<customer>: Ich überlege mir, die Versicherung komplett zu wechseln. Können Sie mir sagen, wie lange meine Kündigungsfrist ist?
<agent>: In Ihrer Police FV-6623-H3 ist eine Kündigung jeweils auf das Ende der Versicherungsperiode mit dreimonatiger Frist vorgesehen.
<customer>: Das heisst, ich bin noch fast ein Jahr gebunden?
<agent>: Ausser bei einem Schadenfall oder einer Prämienänderung – dann gibt es ein ausserordentliches Kündigungsrecht.
<customer>: Hm. Dann warte ich wohl ab, was mit den Prämien nächstes Jahr passiert.
<agent>: Das ist eine Möglichkeit. Wenn Sie möchten, kann ich Ihre Police auf Optimierungspotenzial prüfen, damit ein Wechsel vielleicht gar nicht nötig ist.
<customer>: Nein danke, im Moment will ich nur die Frist wissen.
<agent>: In Ordnung, Herr Keller. Dann bleibt es bei den genannten drei Monaten vor Ablauf.""",
        "topics": ["10"],
        "summary": "Customer inquires about cancellation period of his vehicle insurance because he considers switching. He leaves it at the information for now."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Roth. Noch eine Frage zu meiner Reiseversicherung.
<agent>: Guten Tag Frau Roth, hier ist Luca Steiner. Gerne, was möchten Sie wissen?
<customer>: Deckt meine Police auch den Verlust meines Laptops auf Reisen?
<agent>: Ich sehe in Ihrer Police RV-8954-C5 eine Gepäckversicherung, allerdings mit einem Höchstbetrag pro Einzelgegenstand.
<customer>: Und wie hoch ist der?
<agent>: 2'000 Franken pro Gegenstand.
<customer>: Mein Laptop war teurer.
<agent>: Dann wäre im Schadenfall der Ersatz auf diesen Höchstbetrag begrenzt. Es gibt die Möglichkeit, besonders wertvolle Gegenstände separat zu versichern.
<customer>: Das ist ja wieder kompliziert. Aber gut, dann weiss ich Bescheid.
<agent>: Wenn Sie möchten, kann ich Ihnen Informationen zu einer separaten Elektronikversicherung schicken.
<customer>: Schicken Sie es, entscheiden werde ich später.
<agent>: Sehr gern, an roth@gmail.com.""",
        "topics": ["11"],
        "summary": "Customer asks if her laptop is fully covered while traveling. Luggage insurance has a maximum amount per item; a separate electronics insurance is mentioned as an option."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Weber. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Herr Weber, hier ist Anna Meier von der Vaudoise. Womit kann ich Ihnen helfen?
<customer>: Ich bin gerade umgezogen und frage mich, ob ich alle meine Policen aktualisieren muss.
<agent>: Das ist eine sehr wichtige Frage. Ein Umzug kann verschiedene Auswirkungen auf Ihre Versicherungen haben. Haben Sie Ihre Kundennummer zur Hand?
<customer>: Ja, das ist 52-BH-3847-N2.
<agent>: Danke. Ich sehe hier eine Hausrat-, Privathaftpflicht- und Fahrzeugversicherung. Bei einem Umzug sollten wir mindestens die Adressen aktualisieren.
<customer>: Ändert sich dadurch auch die Prämie?
<agent>: Das kann durchaus sein, je nach Risikozone des neuen Wohnorts. Manchmal wird es günstiger, manchmal teurer.
<customer>: Können Sie das für mich prüfen und mir eine Übersicht schicken?
<agent>: Sehr gerne. Ich sende Ihnen eine Aufstellung aller notwendigen Änderungen an weber@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer inquires about updating his insurance policies after moving. The agent explains potential premium changes and offers to send a comprehensive overview."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Martin. J'ai l'impression qu'il me manque quelque chose dans mes assurances.
<agent>: Bonjour Madame Martin, ici Pascal Tremblay de Vaudoise. Qu'est-ce qui vous préoccupe?
<customer>: Je viens de commencer à travailler en freelance depuis la maison, et je me demande si mon équipement professionnel est couvert.
<agent>: C'est une excellente question. Votre police ménage standard couvre généralement l'équipement privé, mais pas nécessairement l'équipement professionnel.
<customer>: Et qu'est-ce que cela signifie concrètement? Mon ordinateur portable et mon matériel de bureau ne sont pas assurés?
<agent>: Cela dépend de la valeur et de l'usage. Pour un usage professionnel intensif, nous recommandons souvent une extension spéciale.
<customer>: Pouvez-vous me faire une offre pour cela? Je ne veux pas me retrouver sans protection.
<agent>: Bien sûr, je vous prépare une proposition pour une couverture équipement professionnel à domicile. Je vous l'envoie à martin@hotmail.com.""",
        "topics": ["2"],
        "summary": "Customer working as freelancer from home discovers potential coverage gap for professional equipment. Agent prepares special coverage proposal.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Thompson. I'm interested in expanding my insurance coverage with Vaudoise.
<agent>: Hello Mr. Thompson, this is Sarah Dürst from Vaudoise. What type of coverage are you looking for?
<customer>: I just bought a motorcycle and I need insurance for it. I already have car insurance with you.
<agent>: Excellent! Since you're already our customer, we can offer attractive package discounts. What type of motorcycle did you purchase?
<customer>: It's a touring bike, mainly for weekend trips and holidays.
<agent>: For touring bikes, I'd recommend comprehensive coverage including roadside assistance for longer trips. Would you like me to prepare a quote?
<customer>: Yes, please. But I want to see different options - basic and comprehensive coverage.
<agent>: Perfect. I'll prepare both variants and send them to thompson@gmail.com. You can then choose what fits your needs and budget best.""",
        "topics": ["3"],
        "summary": "Existing customer wants motorcycle insurance for his new touring bike. Agent prepares quotes for both basic and comprehensive coverage options.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Müller. Ich bin sehr unzufrieden mit der Bearbeitung meines Schadensfalls.
<agent>: Guten Tag Frau Müller, hier ist Marc Ducret. Es tut mir leid, dass Sie unzufrieden sind. Um welchen Schadenfall handelt es sich?
<customer>: Es geht um den Einbruchschaden, Referenz SV-7429-X1. Die Schadensregulierung zieht sich schon seit Wochen hin.
<agent>: Lassen Sie mich den Fall aufrufen... Ich sehe, dass noch zusätzliche Belege angefordert wurden. Haben Sie diese eingereicht?
<customer>: Ja, schon vor zwei Wochen! Aber seither höre ich nichts mehr. Das ist doch unmöglich.
<agent>: Sie haben recht, das ist zu lange. Ich sehe die Belege im System, aber sie wurden noch nicht bearbeitet. Das hätte schneller gehen müssen.
<customer>: Ich brauche das Geld dringend, um die Schäden zu reparieren. Wann kann ich endlich mit einer Entscheidung rechnen?
<agent>: Ich priorisiere Ihren Fall sofort und sorge dafür, dass die Bearbeitung bis spätestens übermorgen abgeschlossen ist. Sie erhalten eine schriftliche Bestätigung.""",
        "topics": ["4"],
        "summary": "Customer frustrated with delayed burglary claim processing despite submitting required documents weeks ago. Agent prioritizes the case for immediate completion."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Dubois. J'appelle pour suivre mon dossier sinistre.
<agent>: Bonjour Monsieur Dubois, ici Luca Steiner de Vaudoise. Quel est le numéro de référence?
<customer>: SN-8856-P4. Il s'agit des dégâts de grêle sur ma voiture.
<agent>: Je vois votre dossier. L'expert a terminé son évaluation et l'offre de règlement a été préparée.
<customer>: Et pourquoi ne l'ai-je pas encore reçue?
<agent>: Elle devait vous être envoyée hier. Permettez-moi de vérifier... Il semble y avoir eu un retard dans l'envoi postal.
<customer>: C'est toujours pareil avec vous. On doit constamment relancer.
<agent>: Je comprends votre frustration. Je vous envoie immédiatement l'offre par email et je vérifie que le courrier soit aussi expédié aujourd'hui.
<customer>: Faites donc cela. Et j'espère que le montant est correct cette fois.
<agent>: L'expert a évalué tous les dommages visibles. Si vous n'êtes pas d'accord, nous pouvons discuter d'une contre-expertise.""",
        "topics": ["5"],
        "summary": "Customer follows up on hail damage claim. Settlement offer was delayed in postal delivery, agent sends it immediately by email."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Johnson. I have a question about my premium payment.
<agent>: Good morning Mrs. Johnson, this is Nora Widmer from Vaudoise. How can I assist you?
<customer>: I received a bill that seems much higher than usual. I'm wondering if there's been a mistake.
<agent>: Let me check your account. Could you provide me with your policy number?
<customer>: It's PZ-4712-M9.
<agent>: Thank you. I see there was indeed a premium adjustment due to a claim you made last year, which affected your no-claims bonus.
<customer>: But I thought my bonus protection would prevent that?
<agent>: Your bonus protection covers one claim per year, but you had two claims in the same period, so the second one affected your premium.
<customer>: Nobody told me about this! I would have handled the smaller claim myself if I had known.
<agent>: I understand your concern. Let me send you a detailed breakdown showing how your premium was calculated, so you can see exactly what happened.""",
        "topics": ["6"],
        "summary": "Customer questions higher premium bill. Agent explains impact of multiple claims on no-claims bonus and offers detailed calculation breakdown."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Schmidt. Ich habe Fragen zu meiner Gesundheitsunterstützung.
<agent>: Guten Tag Herr Schmidt, hier ist Anna Meier. Womit kann ich Ihnen helfen?
<customer>: Mein Physiotherapeut hat mir eine längere Behandlung empfohlen, und ich möchte wissen, was übernommen wird.
<agent>: Schauen wir in Ihre Police GS-5578-K2. Sie haben eine Zusatzversicherung mit Physiotherapie-Deckung.
<customer>: Gibt es eine Begrenzung der Anzahl Sitzungen?
<agent>: Pro Jahr sind 30 Sitzungen gedeckt, vorausgesetzt sie sind ärztlich verordnet.
<customer>: Mein Arzt empfiehlt 35 Sitzungen. Was passiert mit den zusätzlichen fünf?
<agent>: Die können über die Grundversicherung laufen oder Sie zahlen sie selbst. Ich empfehle, zuerst die Kostengutsprache für alle 35 Sitzungen zu beantragen.
<customer>: Können Sie mir die nötigen Formulare schicken?
<agent>: Gerne. Ich sende Ihnen alle Unterlagen an schmidt@gmail.com.""",
        "topics": ["7"],
        "summary": "Customer inquires about physiotherapy coverage limits. Agent explains 30 sessions are covered and helps with authorization process for additional sessions."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Petit. Mon auto est tombée en panne sur l'autoroute.
<agent>: Bonjour Madame Petit, ici Yann Morel de l'assistance Vaudoise. Êtes-vous en sécurité?
<customer>: Oui, je suis sur la bande d'arrêt d'urgence avec les feux de détresse allumés.
<agent>: Parfait. Où vous trouvez-vous exactement?
<customer>: Sur l'A1 direction Genève, juste après la sortie de Morges.
<agent>: Votre numéro de police est PH-9341-R7, c'est bien cela?
<customer>: Oui, c'est correct. Le moteur s'est arrêté d'un coup et ne redémarre plus.
<agent>: J'organise immédiatement un dépanneur. Il devrait arriver dans 30 à 40 minutes maximum.
<customer>: Et si la réparation n'est pas possible sur place?
<agent>: Alors on remorque votre véhicule vers un garage partenaire. Les frais sont couverts par votre assistance routière.
<customer>: Parfait, merci. J'attends alors le dépanneur.
<agent>: Il vous appellera quelques minutes avant d'arriver, Madame Petit.""",
        "topics": ["8"],
        "summary": "Customer's car breaks down on highway. Roadside assistance is dispatched with full coverage for towing and repair services."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Williams. I have a question about my property insurance.
<agent>: Good afternoon Mr. Williams, this is Pascal Tremblay from Vaudoise. What can I help you with?
<customer>: We're planning to install solar panels on our roof. Does this affect our property insurance?
<agent>: That's a great question. Solar panel installations can indeed impact your coverage. Let me check your policy HR-6684-L5.
<customer>: Do I need to inform you before the installation?
<agent>: Yes, it's important to notify us as it increases the value of your property and changes the risk profile slightly.
<customer>: Will this increase my premium significantly?
<agent>: Usually the increase is minimal because solar panels are well-secured installations. But the coverage increase protects your investment.
<customer>: That makes sense. What information do you need from me?
<agent>: I'll send you a simple form to complete with installation details and value. Then we can adjust your policy accordingly.""",
        "topics": ["9"],
        "summary": "Customer planning solar panel installation asks about property insurance impact. Agent explains notification requirements and minimal premium increase.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Hofmann. Ich habe eine Frage zur Fahrzeugversicherung.
<agent>: Guten Tag Frau Hofmann, hier ist Sarah Dürst. Worum geht es?
<customer>: Meine Tochter hat gerade den Führerschein gemacht. Kann ich sie in meine Versicherung aufnehmen?
<agent>: Ja, das ist möglich. Allerdings wird sich die Prämie erhöhen, da Fahranfänger ein höheres Risiko darstellen.
<customer>: Um wie viel ungefähr?
<agent>: Das hängt vom Alter und anderen Faktoren ab. Für Ihre Police FV-7823-D6 würde ich schätzen, etwa 40-60% Aufschlag.
<customer>: Das ist aber teuer! Gibt es Alternativen?
<agent>: Wir könnten eine separate Police für Ihre Tochter eröffnen oder schauen, ob es günstigere Fahranfänger-Programme gibt.
<customer>: Schicken Sie mir bitte beide Varianten zur Ansicht.
<agent>: Sehr gerne, ich erstelle Ihnen eine Vergleichsrechnung und sende sie an hofmann@gmail.com.""",
        "topics": ["10"],
        "summary": "Customer wants to add newly licensed daughter to car insurance. Agent explains premium increase and offers comparison between adding to existing policy vs separate coverage."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Brown. I'm calling about my travel insurance.
<agent>: Hello Ms. Brown, this is Luca Steiner from Vaudoise. How can I help you?
<customer>: I'm planning a ski trip to the Alps next month. Does my travel insurance cover winter sports?
<agent>: Let me check your policy RV-1247-Q3... Yes, you have winter sports coverage included, but with certain conditions.
<customer>: What kind of conditions?
<agent>: The coverage applies to marked ski slopes and recognized winter sports areas. Off-piste skiing requires additional coverage.
<customer>: I'm only planning to ski on regular slopes. What about ski equipment?
<agent>: Your policy covers ski equipment up to 1,500 francs per person against theft or damage.
<customer>: That should be sufficient. Do I need to do anything special before the trip?
<agent>: No special preparation needed. Just make sure to keep receipts for any equipment rentals or purchases for potential claims.""",
        "topics": ["11"],
        "summary": "Customer confirms travel insurance coverage for upcoming ski trip. Agent explains winter sports coverage conditions and equipment protection limits."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Zimmermann. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Zimmermann, hier ist Marc Ducret. Wie kann ich Ihnen helfen?
<customer>: Ich habe geheiratet und möchte meine Frau als Begünstigte eintragen lassen.
<agent>: Herzlichen Glückwunsch zur Hochzeit! Das können wir gerne anpassen. Haben Sie Ihre Policennummer?
<customer>: Ja, LV-8834-F7.
<agent>: Danke. Möchten Sie Ihre Frau als alleinige Begünstigte eintragen oder prozentual aufteilen?
<customer>: Als alleinige Begünstigte. Gibt es dabei etwas zu beachten?
<agent>: Bei einer Änderung der Begünstigung empfehlen wir auch zu prüfen, ob die Versicherungssumme noch angemessen ist.
<customer>: Das ist ein guter Punkt. Können Sie mir eine Einschätzung geben?
<agent>: Gerne. Ich sende Ihnen das Änderungsformular und eine Bedarfsanalyse für die Versicherungssumme an zimmermann@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to update life insurance beneficiary after marriage. Agent processes change and offers to review adequacy of insurance amount."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Leroy. J'ai une question sur mon assurance objets de valeur.
<agent>: Bonjour Madame Leroy, ici Anna Meier de Vaudoise. Que puis-je faire pour vous?
<customer>: J'ai hérité de bijoux de famille et je voudrais savoir s'ils sont automatiquement couverts.
<agent>: Les nouveaux objets de valeur ne sont pas automatiquement couverts. Il faut les déclarer et les faire évaluer.
<customer>: Comment procède-t-on pour l'évaluation?
<agent>: Vous devez faire appel à un expert bijoutier agréé qui établira une estimation officielle de la valeur.
<customer>: Et cela coûte cher?
<agent>: L'expertise coûte généralement entre 100 et 200 francs selon la complexité, mais c'est indispensable pour la couverture.
<customer>: D'accord. Pouvez-vous me donner les coordonnées d'experts agréés?
<agent>: Bien sûr, je vous envoie une liste d'experts dans votre région à leroy@gmail.com.""",
        "topics": ["13"],
        "summary": "Customer inherited family jewelry and asks about insurance coverage. Agent explains evaluation requirement by certified expert and provides expert list.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Wagner. Ich habe eine allgemeine Frage zu Vaudoise.
<agent>: Guten Tag Frau Wagner, hier ist Pascal Tremblay. Womit kann ich Ihnen behilflich sein?
<customer>: Ich überlege, alle meine Versicherungen bei einem Anbieter zu bündeln. Welche Vorteile bietet das?
<agent>: Eine Bündelung bringt mehrere Vorteile: Rabatte, einfachere Verwaltung und einen zentralen Ansprechpartner.
<customer>: Wie hoch sind die Rabatte normalerweise?
<agent>: Je nach Produktkombination können Sie zwischen 5 und 15 Prozent auf die Gesamtprämie sparen.
<customer>: Das klingt interessant. Ich habe derzeit Auto-, Hausrat- und Haftpflichtversicherung bei verschiedenen Anbietern.
<agent>: Das wären perfekte Kandidaten für eine Bündelung. Soll ich Ihnen eine unverbindliche Vergleichsrechnung erstellen?
<customer>: Ja, gerne. Aber ohne Verkaufsdruck bitte.
<agent>: Selbstverständlich. Sie erhalten nur Zahlen und Fakten zur eigenen Entscheidung. Ich sende die Berechnung an wagner@gmail.com.""",
        "topics": ["1"],
        "summary": "Customer considers bundling all insurance policies with Vaudoise. Agent explains benefits including discounts and offers comparison calculation."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Davis. I think I might have a gap in my insurance coverage.
<agent>: Hello Mr. Davis, this is Nora Widmer from Vaudoise. What makes you think there might be a gap?
<customer>: I started a small consulting business from home and I'm not sure if my professional liability is covered.
<agent>: That's an important concern. Personal liability insurance typically doesn't cover professional activities. Let me check your current coverage.
<customer>: My policy number is UD-5591-H8.
<agent>: I see you have personal liability but no professional liability insurance. For consulting work, you'd need a separate business liability policy.
<customer>: I was afraid of that. How urgent is this?
<agent>: Very urgent. If a client makes a claim against your consulting services, you wouldn't be protected without proper coverage.
<customer>: Can you prepare a quote for professional liability insurance?
<agent>: Absolutely. I'll prepare a quote specifically for consulting services and send it to davis@hotmail.com today.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for new consulting business. Personal liability doesn't cover professional activities, so separate business liability insurance is needed urgently."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Becker. Ich interessiere mich für eine neue Versicherung.
<agent>: Guten Tag Herr Becker, hier ist Sarah Dürst von der Vaudoise. Welche Art von Versicherung schwebt Ihnen vor?
<customer>: Ich kaufe ein Wohnmobil für den Ruhestand und brauche dafür eine passende Versicherung.
<agent>: Glückwunsch zum neuen Wohnmobil! Dafür gibt es spezielle Campingfahrzeug-Versicherungen mit erweiterten Leistungen.
<customer>: Was ist denn anders als bei einer normalen Fahrzeugversicherung?
<agent>: Zum Beispiel Campingzubehör-Versicherung, erweiterte Pannenhilfe in ganz Europa und Schutz bei längeren Standzeiten.
<customer>: Das klingt sinnvoll. Ich plane längere Reisen durch Europa.
<agent>: Dann ist eine umfassende Europa-Deckung besonders wichtig. Soll ich Ihnen verschiedene Deckungsoptionen zusammenstellen?
<customer>: Ja, bitte. Schicken Sie mir eine detaillierte Offerte mit verschiedenen Varianten.
<agent>: Sehr gerne. Ich erstelle Ihnen passende Angebote für Ihr Wohnmobil und sende sie an becker@gmail.com.""",
        "topics": ["3"],
        "summary": "Customer needs insurance for new motorhome for retirement travels. Agent explains specialized camping vehicle insurance with European coverage options."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Moreau. Je suis mécontent du règlement de mon sinistre.
<agent>: Bonjour Monsieur Moreau, ici Marc Ducret. Je suis désolé d'apprendre votre mécontentement. De quel sinistre s'agit-il?
<customer>: Dégâts d'eau dans ma cave, référence SV-2847-K9. Vous refusez une partie des dommages.
<agent>: Laissez-moi consulter le dossier... Je vois qu'une partie a été classée comme dommages préexistants.
<customer>: C'est ridicule! L'eau venait de la canalisation du voisin, pas de chez moi.
<agent>: Je comprends votre position. L'expert a constaté que certains dégâts étaient antérieurs à la fuite du voisin.
<customer>: Je ne peux pas accepter cela. Je veux une contre-expertise.
<agent>: C'est votre droit. Nous pouvons organiser une seconde expertise par un expert indépendant.
<customer>: Faites-le. Et cette fois, je veux être présent lors de l'inspection.
<agent>: Bien sûr, vous serez informé de tous les rendez-vous. Je lance la procédure immédiatement.""",
        "topics": ["4"],
        "summary": "Customer disputes water damage claim settlement where part was classified as pre-existing damage. Second independent expert evaluation is requested."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Taylor. I'm calling for an update on my claim.
<agent>: Good afternoon Mrs. Taylor, this is Luca Steiner from Vaudoise. What's your claim reference number?
<customer>: SN-3765-Q1. It's for the storm damage to my garden shed.
<agent>: Let me check... I see that the adjuster's report was completed and approved yesterday.
<customer>: Finally! When will I receive the settlement?
<agent>: The payment has been processed and should reach your account within 2-3 business days.
<customer>: Great. Will you also cover the cleanup costs for the debris?
<agent>: Yes, the cleanup costs are included in the settlement amount as they were part of the original damage assessment.
<customer>: Perfect. I was worried I'd have to pay for that separately.
<agent>: No, everything is covered as agreed. You'll receive a detailed settlement statement by email today.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on storm damage claim. Settlement including cleanup costs has been processed and will arrive within days."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Fischer. Ich habe eine Frage zu meiner Prämienrechnung.
<agent>: Guten Tag Herr Fischer, hier ist Anna Meier von der Vaudoise. Was ist unklar bei Ihrer Rechnung?
<customer>: Ich zahle seit Jahren pünktlich, aber bekomme nie einen Rabatt für treue Kunden.
<agent>: Lassen Sie mich Ihre Police PZ-6739-N4 prüfen... Sie haben bereits den maximalen Schadenfreiheitsrabatt.
<customer>: Aber andere Versicherer bieten zusätzliche Treueboni an.
<agent>: Das stimmt. Wir haben andere Vorteile wie kostenlose Serviceleistungen und bevorzugte Schadensbearbeitung für langjährige Kunden.
<customer>: Das ist mir nicht bekannt. Können Sie mir diese Leistungen auflisten?
<agent>: Gerne. Ich sende Ihnen eine Übersicht aller Zusatzleistungen, die Sie als Bestandskunde erhalten.
<customer>: Das wäre hilfreich. Vielleicht übersehe ich ja etwas.
<agent>: Ich bin sicher, da sind einige Leistungen dabei, die Sie noch nicht kannten. Die Übersicht geht an fischer@gmail.com.""",
        "topics": ["6"],
        "summary": "Long-term customer asks about loyalty discounts. Agent explains existing maximum discount and additional customer benefits for loyal clients."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Girard. J'ai des questions sur mes prestations santé.
<agent>: Bonjour Madame Girard, ici Nora Widmer. En quoi puis-je vous aider?
<customer>: Mon médecin m'a prescrit des séances de naturopathie. Est-ce que c'est couvert?
<agent>: Laissez-moi vérifier votre police GS-4493-T8... Vous avez une couverture médecines alternatives avec certaines conditions.
<customer>: Quelles conditions exactement?
<agent>: Le praticien doit être reconnu par l'ASCA ou le RME, et il y a un plafond annuel de 1000 francs.
<customer>: Et comment savoir si mon naturopathe est reconnu?
<agent>: Vous pouvez vérifier sur les sites web ASCA ou RME, ou simplement demander à votre praticien ses certifications.
<customer>: D'accord. Et si je dépasse les 1000 francs?
<agent>: Alors les frais supplémentaires seraient à votre charge. Je vous envoie la liste des praticiens reconnus dans votre région pour référence.""",
        "topics": ["7"],
        "summary": "Customer inquires about naturopathy coverage. Agent explains recognition requirements and annual limits for alternative medicine practitioners."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Anderson. I need emergency roadside assistance.
<agent>: Hello Mr. Anderson, this is Yann Morel from Vaudoise assistance. Are you in a safe location?
<customer>: Yes, I'm in a parking lot. My car won't start and I have an important meeting in an hour.
<agent>: I understand the urgency. What's your location and policy number?
<customer>: I'm at the shopping center in Lausanne, policy PH-7741-S3.
<agent>: Perfect, I can dispatch a technician immediately. They should arrive within 20-25 minutes.
<customer>: What if they can't fix it on site?
<agent>: If it can't be repaired, we can provide a replacement vehicle so you can make your meeting.
<customer>: You have replacement cars available?
<agent>: Yes, your policy includes replacement vehicle service for mechanical breakdowns. The technician will arrange it if needed.
<customer>: That's a relief. Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs urgent roadside assistance before important meeting. Quick dispatch arranged with replacement vehicle option if repair isn't possible."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Koch. Ich habe eine Frage zur Gebäudeversicherung.
<agent>: Guten Tag Frau Koch, hier ist Pascal Tremblay von der Vaudoise. Wobei kann ich helfen?
<customer>: Wir haben einen Swimming Pool bauen lassen. Muss das in der Versicherung angemeldet werden?
<agent>: Das ist eine wichtige Frage. Ein Pool erhöht den Gebäudewert und sollte definitiv gemeldet werden.
<customer>: Wird dadurch die Prämie viel teurer?
<agent>: Die Erhöhung ist normalerweise moderat, da Pools fest installiert und gegen die meisten Risiken gut geschützt sind.
<customer>: Was ist mit der Haftpflicht? Wenn jemand im Pool verunglückt?
<agent>: Das wäre über Ihre Privathaftpflichtversicherung gedeckt, vorausgesetzt Sie haben den Pool ordnungsgemäß gesichert.
<customer>: Können Sie beide Policen entsprechend anpassen?
<agent>: Gerne. Ich erstelle Ihnen die Anpassungen und sende sie zur Prüfung an koch@gmail.com.""",
        "topics": ["9"],
        "summary": "Customer reports new swimming pool construction. Agent explains building insurance adjustment and liability coverage requirements."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Bernard. Ma voiture a été volée cette nuit.
<agent>: Bonjour Monsieur Bernard, ici Sarah Dürst de Vaudoise. Je suis désolée d'apprendre cela. Avez-vous déjà contacté la police?
<customer>: Oui, j'ai déposé plainte ce matin. Le numéro de plainte est 2024-445-891.
<agent>: Parfait. Votre numéro de police est FV-5529-J6, c'est bien cela?
<customer>: Oui. Qu'est-ce que je dois faire maintenant?
<agent>: Je vais ouvrir un dossier sinistre immédiatement. Vous devez nous envoyer une copie de la plainte et nous donner tous les détails du vol.
<customer>: La voiture était fermée à clé devant chez moi. Il n'y avait rien d'anormal.
<agent>: D'accord. Avez-vous encore tous les clés en votre possession?
<customer>: Oui, toutes les clés étaient à la maison. Comment ça se passe pour le remboursement?
<agent>: Nous attendons d'abord que la police termine son enquête, puis nous procédons selon la valeur actuelle de votre véhicule.""",
        "topics": ["10"],
        "summary": "Customer reports car theft that occurred overnight. Agent opens claim file and explains process including police investigation and current value assessment."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Ms. Wilson. I have a question about my travel insurance.
<agent>: Good afternoon Ms. Wilson, this is Marc Ducret from Vaudoise. What would you like to know?
<customer>: I'm pregnant and wondering if this affects my travel insurance for an upcoming trip.
<agent>: Congratulations! Pregnancy does have some implications for travel insurance. Let me check your policy RV-8822-D7.
<customer>: I'm in my second trimester and planning to travel to Italy next month.
<agent>: For pregnancy-related coverage, there are specific conditions. Normal pregnancy isn't considered an illness, but complications could be covered.
<customer>: What if I need medical attention while abroad?
<agent>: Emergency medical care is covered, but routine pregnancy check-ups during travel are not included in standard coverage.
<customer>: Should I consider additional coverage?
<agent>: I'd recommend discussing with your doctor first about travel safety, then we can assess if additional pregnancy-related coverage would be beneficial.""",
        "topics": ["11"],
        "summary": "Pregnant customer inquires about travel insurance coverage. Agent explains emergency vs routine care coverage and suggests medical consultation first."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Richter. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Herr Richter, hier ist Luca Steiner. Wie kann ich helfen?
<customer>: Ich bin arbeitslos geworden und kann mir die Prämien nicht mehr leisten. Was sind meine Optionen?
<agent>: Das tut mir leid zu hören. Es gibt mehrere Möglichkeiten: Prämienbefreiung, Reduktion der Versicherungssumme oder temporäre Aussetzung.
<customer>: Was bedeutet Prämienbefreiung genau?
<agent>: Bei nachgewiesener Arbeitslosigkeit können wir die Prämienzahlung für bis zu 12 Monate aussetzen, ohne dass der Vertrag verfällt.
<customer>: Das wäre ideal. Welche Unterlagen brauchen Sie?
<agent>: Eine Bescheinigung des RAV und einen Nachweis über das Arbeitslosengeld. Der Schutz bleibt während dieser Zeit bestehen.
<customer>: Perfekt. Wo kann ich diese Unterlagen einreichen?
<agent>: Ich sende Ihnen das entsprechende Formular und die Anweisungen an richter@gmail.com.""",
        "topics": ["12"],
        "summary": "Unemployed customer can't afford life insurance premiums. Agent explains premium waiver option for unemployment with continued coverage.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. Roberts. I have a question about my valuables insurance.
<agent>: Hello Mrs. Roberts, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm going on vacation and want to take some jewelry with me. Are they covered while traveling?
<agent>: Your valuables policy WV-7734-X2 includes worldwide coverage, but with certain security requirements while traveling.
<customer>: What kind of security requirements?
<agent>: Items should not be left unattended in vehicles, and hotel safes should be used when available. There are also coverage limits per item.
<customer>: What if the hotel doesn't have a safe?
<agent>: Then you should keep valuable items with you at all times or consider leaving very expensive pieces at home for this trip.
<customer>: That makes sense. Is there anything else I should know?
<agent>: Take photos of the jewelry before traveling and keep receipts. This helps with any potential claims.""",
        "topics": ["13"],
        "summary": "Customer asks about jewelry coverage while traveling. Agent explains worldwide coverage with security requirements and documentation recommendations."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Neumann. Ich habe eine allgemeine Frage zu meinen Versicherungen.
<agent>: Guten Tag Frau Neumann, hier ist Pascal Tremblay. Was beschäftigt Sie?
<customer>: Meine Nachbarin hatte einen Wasserschaden und war wochenlang ohne Heizung. Bin ich dagegen versichert?
<agent>: Das ist eine wichtige Überlegung. Schauen wir in Ihre Hausratversicherung HR-9966-L1, ob zusätzliche Lebenshaltungskosten gedeckt sind.
<customer>: Was sind zusätzliche Lebenshaltungskosten?
<agent>: Wenn Ihre Wohnung unbewohnbar wird, zahlen wir Hotelkosten oder Miete für eine Ersatzwohnung für eine begrenzte Zeit.
<customer>: Wie lange ist diese begrenzte Zeit?
<agent>: In Ihrer Police sind bis zu 12 Monate gedeckt, je nach Umfang der Schäden und Reparaturdauer.
<customer>: Das beruhigt mich. Muss ich bestimmte Hotels wählen?
<agent>: Nein, aber die Kosten müssen angemessen sein. Wir erstatten bis zur Höhe Ihrer normalen Wohnkosten plus einem Aufschlag.
<customer>: Gut zu wissen. Danke für die Erklärung.""",
        "topics": ["1"],
        "summary": "Customer asks about coverage for alternative accommodation after hearing neighbor's water damage story. Agent explains additional living costs coverage terms."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Fabre. Je pense avoir un besoin d'assurance non couvert.
<agent>: Bonjour Monsieur Fabre, ici Sarah Dürst. Qu'est-ce qui vous préoccupe?
<customer>: Je fais de la photographie professionnelle et mon équipement coûte très cher. Mon assurance ménage ne suffit pas.
<agent>: Effectivement, l'équipement professionnel nécessite souvent une couverture spécialisée. Quelle est la valeur approximative?
<customer>: Environ 25'000 francs en appareils photos, objectifs et équipement d'éclairage.
<agent>: Pour cette valeur, nous recommandons une assurance équipement professionnel avec couverture mondiale.
<customer>: Mondiale? Pourquoi?
<agent>: Pour un photographe, l'équipement voyage beaucoup. Il faut une protection contre le vol, les dommages et la perte, même à l'étranger.
<customer>: Cela me semble logique. Pouvez-vous me faire une offre?
<agent>: Bien sûr, je vous prépare une proposition pour assurance équipement professionnel photographique. Je l'envoie à fabre@gmail.com.""",
        "topics": ["2"],
        "summary": "Professional photographer needs specialized equipment insurance beyond standard household coverage. Agent prepares worldwide professional equipment proposal."
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Clarke. I'm interested in business insurance for my new company.
<agent>: Good morning Mr. Clarke, this is Marc Ducret from Vaudoise. Congratulations on your new business! What type of company are you starting?
<customer>: It's a small IT consulting firm. I'll be working mostly with corporate clients on software projects.
<agent>: For IT consulting, you'll need professional liability insurance, general liability, and possibly cyber liability coverage.
<customer>: Cyber liability? What's that for?
<agent>: It protects against data breaches, cyber attacks, and privacy violations. Very important for IT companies handling client data.
<customer>: That makes sense. How much does this typically cost for a small firm?
<agent>: For a startup IT consulting firm, we're typically looking at 1,500 to 3,000 francs annually for a comprehensive package.
<customer>: That seems reasonable. Can you prepare a detailed quote?
<agent>: Absolutely. I'll create a tailored business insurance package for your IT consulting firm and send it to clarke@gmail.com.""",
        "topics": ["3"],
        "summary": "Entrepreneur needs business insurance for new IT consulting firm. Agent explains professional, general, and cyber liability coverage needs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Weber. Ich bin extrem verärgert über die Schadensbearbeitung.
<agent>: Guten Tag Frau Weber, hier ist Luca Steiner. Es tut mir leid zu hören, dass Sie verärgert sind. Was ist passiert?
<customer>: Sturmschaden am Dach, Referenz SV-5641-M2. Die Reparatur wurde abgelehnt wegen angeblicher Vorschäden.
<agent>: Lassen Sie mich den Fall prüfen... Ich sehe, dass der Gutachter Altersschwäche der Dachziegel festgestellt hat.
<customer>: Das Dach ist erst fünf Jahre alt! Das ist doch kein Alter.
<agent>: Sie haben recht, das ist sehr jung für ein Dach. Haben Sie noch Garantieunterlagen vom Dachdecker?
<customer>: Natürlich! Die habe ich auch schon eingereicht, aber niemand hat darauf reagiert.
<agent>: Das hätte beachtet werden müssen. Ich lasse den Fall von unserem Bauschadenexperten neu bewerten.
<customer>: Endlich mal jemand, der zuhört! Wann kann ich mit einer Antwort rechnen?
<agent>: Bis Ende der Woche haben Sie eine neue Einschätzung. Entschuldigen Sie die Unannehmlichkeiten.""",
        "topics": ["4"],
        "summary": "Customer frustrated about roof damage claim rejection due to alleged pre-existing damage on 5-year-old roof. Case referred to construction damage expert for reevaluation."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Rousseau. Je voudrais un point sur mon sinistre.
<agent>: Bonjour Madame Rousseau, ici Anna Meier de Vaudoise. Quel est votre numéro de référence?
<customer>: SN-7788-V5. Il s'agit du cambriolage de mon appartement il y a trois semaines.
<agent>: Je vois votre dossier. L'enquête de police est terminée et nous avons reçu le rapport officiel.
<customer>: Parfait. Et maintenant?
<agent>: Nous finalisons l'inventaire des objets volés. Avez-vous d'autres preuves d'achat à nous envoyer?
<customer>: Non, je vous ai tout transmis. Quand vais-je être indemnisée?
<agent>: Le règlement sera effectué dans les 5 jours ouvrables. Vous recevrez d'abord un décompte détaillé.
<customer>: Très bien. Y aura-t-il une franchise à déduire?
<agent>: Oui, votre police prévoit une franchise de 500 francs pour les cambriolages.
<customer>: D'accord, je m'y attendais. Merci pour ces nouvelles rassurantes.""",
        "topics": ["5"],
        "summary": "Customer gets positive update on burglary claim. Police investigation complete, settlement will be processed within 5 business days with standard deductible."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Turner. I have a billing question.
<agent>: Hello Mr. Turner, this is Pascal Tremblay from Vaudoise. What's your billing concern?
<customer>: I switched to annual payments instead of quarterly, but I was charged a processing fee.
<agent>: Let me check your account PZ-8844-R7... I see the payment frequency change and the associated fee.
<customer>: I wasn't told there would be a fee for this change.
<agent>: You're right, that should have been communicated clearly. The fee is typically waived for voluntary changes to less frequent payments.
<customer>: So the fee shouldn't have been charged?
<agent>: Correct. I'll reverse the processing fee and it should appear as a credit on your next statement.
<customer>: Thank you. Will this happen again if I make other changes?
<agent>: No, changes that reduce our administrative costs, like yours, shouldn't incur fees. I'll make sure this is noted in your file.""",
        "topics": ["6"],
        "summary": "Customer charged unexpected fee for switching to annual payments. Agent reverses fee and clarifies that beneficial payment changes shouldn't incur costs."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Maurer. Ich habe Fragen zu Gesundheitsleistungen.
<agent>: Guten Tag Herr Maurer, hier ist Nora Widmer. Womit kann ich helfen?
<customer>: Mein Arzt hat mir Akupunktur verschrieben. Wird das übernommen?
<agent>: Schauen wir in Ihre Police GS-3377-B9... Sie haben eine Zusatzversicherung mit Komplementärmedizin-Deckung.
<customer>: Wie funktioniert die Kostenerstattung?
<agent>: Die Behandlung muss von einem anerkannten Therapeuten durchgeführt werden, dann erstatten wir 70% der Kosten.
<customer>: Bis zu welchem jährlichen Betrag?
<agent>: Ihr Jahresbudget für Komplementärmedizin beträgt 800 Francs.
<customer>: Und wie weiss ich, ob mein Therapeut anerkannt ist?
<agent>: Fragen Sie nach der ASCA- oder RME-Registrierung oder geben Sie mir die Praxisdaten, dann prüfe ich das für Sie.
<customer>: Die Praxis ist in Bern, Dr. Chen, Akupunkturzentrum Bern.
<agent>: Ich prüfe das und melde mich noch heute bei Ihnen zurück.""",
        "topics": ["7"],
        "summary": "Customer asks about acupuncture coverage. Agent explains 70% reimbursement with annual limit and offers to verify therapist recognition status."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Phillips. I need roadside assistance.
<agent>: Good afternoon Mrs. Phillips, this is Yann Morel from Vaudoise assistance. What's your situation?
<customer>: I have a flat tire and I don't have a spare. I'm on the highway near Bern.
<agent>: Are you in a safe location off the roadway?
<customer>: Yes, I'm in a rest area with my hazard lights on.
<agent>: Perfect. Your policy PH-2255-K8 includes tire service. I can send a mobile tire service to replace your flat tire.
<customer>: How long will that take?
<agent>: The tire service should reach you within 45 minutes. They'll have common tire sizes on the truck.
<customer>: What if they don't have my tire size?
<agent>: Then we'll tow you to the nearest tire shop and cover the costs. Your policy includes this service.
<customer>: Great, that takes the stress away. Thank you for the quick help.""",
        "topics": ["8"],
        "summary": "Customer has flat tire on highway with no spare. Mobile tire service dispatched with backup towing option if needed."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Vogel. Es geht um meine Wohngebäudeversicherung.
<agent>: Guten Tag Herr Vogel, hier ist Sarah Dürst. Was kann ich für Sie tun?
<customer>: Wir planen einen Wintergarten anzubauen. Muss das versichert werden?
<agent>: Ja, Anbauten erhöhen die Gebäudeversicherungssumme und sollten gemeldet werden.
<customer>: Der Wintergarten kostet etwa 50.000 Franken. Wie stark steigt dadurch die Prämie?
<agent>: Bei Ihrer Police HR-4488-W6 würde das etwa 120-150 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist weniger als erwartet. Wann muss ich das melden?
<agent>: Idealerweise vor Baubeginn, spätestens bei Fertigstellung. So ist der Anbau von Anfang an mitversichert.
<customer>: Gibt es besondere Auflagen für Wintergärten?
<agent>: Meist nicht, solange er nach den Bauvorschriften errichtet wird. Senden Sie mir die Baupläne, dann prüfe ich das genauer.""",
        "topics": ["9"],
        "summary": "Customer planning winter garden addition asks about building insurance requirements. Agent explains coverage increase and timing for reporting construction."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Blanc. J'ai des questions sur mon assurance auto.
<agent>: Bonjour Madame Blanc, ici Marc Ducret de Vaudoise. Que voulez-vous savoir?
<customer>: Mon fils va bientôt avoir 18 ans et passer son permis. Comment l'assurer?
<agent>: Il y a plusieurs options: l'ajouter à votre police existante ou lui faire une police séparée.
<customer>: Qu'est-ce qui est le plus avantageux?
<agent>: Cela dépend de votre bonus actuel. L'ajouter peut être moins cher, mais risque d'affecter votre bonus en cas d'accident.
<customer>: Et avec une police séparée?
<agent>: Il commence avec un bonus jeune conducteur, mais vos polices restent indépendantes.
<customer>: Peut-être que c'est plus sûr. Pouvez-vous calculer les deux variantes?
<agent>: Bien sûr, je vous prépare une comparaison des coûts et avantages de chaque solution. Je l'envoie à blanc@gmail.com.""",
        "topics": ["10"],
        "summary": "Mother asks about insuring her soon-to-be 18-year-old son. Agent explains options of adding to existing policy vs separate coverage with pros and cons.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Good morning, this is Mr. Green. I have a travel insurance question.
<agent>: Good morning Mr. Green, this is Luca Steiner from Vaudoise. What would you like to know?
<customer>: I'm planning a business trip that might extend into a vacation. Does my travel insurance cover both purposes?
<agent>: Let me check your policy RV-6655-F4... You have standard travel insurance which covers both business and leisure travel.
<customer>: What if the trip gets extended unexpectedly for business reasons?
<agent>: Extensions for business reasons are generally covered, but there's a maximum trip duration limit in your policy.
<customer>: What's my limit?
<agent>: Your policy covers trips up to 180 days. If you need longer coverage, we'd need to arrange extended travel insurance.
<customer>: That should be plenty. Is there anything special I need to do for combined business-leisure trips?
<agent>: No special requirements, the coverage is the same regardless of the purpose of your travel.""",
        "topics": ["11"],
        "summary": "Customer asks about travel insurance for combined business-leisure trip. Standard coverage applies to both purposes with 180-day maximum duration."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Lang. Ich rufe wegen meiner Lebensversicherung an.
<agent>: Guten Tag Frau Lang, hier ist Anna Meier. Wie kann ich Ihnen helfen?
<customer>: Meine finanzielle Situation hat sich verbessert und ich möchte die Versicherungssumme erhöhen.
<agent>: Das freut mich für Sie! Schauen wir uns Ihre Police LV-7711-Q3 an. Um wie viel möchten Sie erhöhen?
<customer>: Von 150.000 auf 250.000 Franken.
<agent>: Das ist eine substanzielle Erhöhung. Dafür ist normalerweise eine neue Gesundheitsprüfung erforderlich.
<customer>: Auch wenn ich schon Kunde bin?
<agent>: Ja, bei Erhöhungen über 50.000 Franken ist eine Gesundheitsprüfung Standard, unabhängig von der bestehenden Kundenbeziehung.
<customer>: Wie läuft das ab?
<agent>: Zuerst füllen Sie einen Gesundheitsfragebogen aus, möglicherweise folgt dann eine ärztliche Untersuchung.
<customer>: Schicken Sie mir die Unterlagen zu. Ich bin gesund und mache mir keine Sorgen.
<agent>: Sehr gerne. Die Unterlagen für die Erhöhung gehen an lang@gmail.com.""",
        "topics": ["12"],
        "summary": "Customer wants to increase life insurance sum due to improved financial situation. Agent explains health examination requirements for substantial increases."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Stone. I have a question about my valuables insurance.
<agent>: Hello Mr. Stone, this is Pascal Tremblay from Vaudoise. How can I help you?
<customer>: I collect vintage watches and some have appreciated significantly in value. Should I update my coverage?
<agent>: Absolutely! Appreciated items should definitely be revalued for proper coverage. When was your last appraisal?
<customer>: About three years ago. Some pieces have doubled in value since then.
<agent>: Then an update is overdue. Underinsurance could result in reduced payouts in case of loss.
<customer>: What's the process for updating values?
<agent>: You'll need fresh appraisals from certified watch experts. We can provide a list of recognized appraisers.
<customer>: That makes sense. Will my premiums increase significantly?
<agent>: Premiums will adjust to reflect the new values, but it's better to pay slightly more for proper coverage than risk major losses.
<customer>: You're right. Please send me the appraiser list and update forms.""",
        "topics": ["13"],
        "summary": "Vintage watch collector needs to update valuables coverage after significant appreciation. Agent emphasizes importance of current appraisals and offers appraiser list.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Huber. Ich habe eine grundsätzliche Frage zu Versicherungen.
<agent>: Guten Tag Herr Huber, hier ist Sarah Dürst. Was beschäftigt Sie?
<customer>: Ich lebe seit kurzem allein nach der Scheidung und frage mich, welche Versicherungen ich wirklich brauche.
<agent>: Das ist eine wichtige Überprüfung nach einer Lebensveränderung. Welche Versicherungen haben Sie derzeit?
<customer>: Auto, Hausrat und Privathaftpflicht. Meine Ex-Frau hatte immer die Übersicht.
<agent>: Das ist eine solide Grundausstattung. Haben Sie Kinder oder Unterhaltsverpflichtungen?
<customer>: Zwei Kinder, ja. Ich zahle Unterhalt.
<agent>: Dann könnte eine Lebensversicherung sinnvoll sein, um die Unterhaltszahlungen abzusichern.
<customer>: Daran habe ich nicht gedacht. Können Sie mir eine Bedarfsanalyse machen?
<agent>: Gerne erstelle ich Ihnen eine individuelle Bedarfsanalyse basierend auf Ihrer neuen Lebenssituation.""",
        "topics": ["1"],
        "summary": "Recently divorced customer reviews insurance needs for new life situation with children and alimony obligations. Agent offers comprehensive needs analysis.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Dupont. Je crois avoir une lacune dans mes assurances.
<agent>: Bonjour Madame Dupont, ici Marc Ducret. Quelle lacune suspectez-vous?
<customer>: J'ai commencé à faire de la location Airbnb dans ma maison secondaire. Est-ce que c'est couvert?
<agent>: C'est une excellente question. La location courte durée n'est généralement pas couverte par l'assurance habitation standard.
<customer>: Qu'est-ce que cela signifie concrètement?
<agent>: En cas de dommages causés par des locataires Airbnb, votre assurance pourrait refuser la prise en charge.
<customer>: C'est embêtant! Que puis-je faire?
<agent>: Nous avons des extensions spéciales pour location courte durée qui couvrent ces risques spécifiques.
<customer>: Et pour la responsabilité civile si un locataire se blesse?
<agent>: Cela aussi nécessite une couverture étendue. Je vous prépare une offre complète pour activité Airbnb.
<customer>: Faites cela rapidement, j'ai déjà des réservations pour le mois prochain.""",
        "topics": ["2"],
        "summary": "Customer discovers coverage gap for Airbnb rental activity in secondary home. Standard home insurance doesn't cover short-term rentals; special extension needed urgently.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mrs. Harris. I'm interested in additional insurance products.
<agent>: Good afternoon Mrs. Harris, this is Nora Widmer from Vaudoise. What type of additional coverage interests you?
<customer>: I'm thinking about legal protection insurance. I've been having some disputes with contractors lately.
<agent>: Legal protection can be very valuable, especially if you frequently deal with service providers. What type of disputes are you facing?
<customer>: Mainly construction and renovation issues. Poor workmanship and contract disagreements.
<agent>: Legal protection insurance would cover consultation with lawyers and court costs for such disputes.
<customer>: Does it cover ongoing disputes or only new ones after the policy starts?
<agent>: Only disputes that arise after the policy effective date. Ongoing issues wouldn't be covered.
<customer>: That's fair. How much does legal protection typically cost?
<agent>: For comprehensive legal protection, you're looking at around 300-400 francs annually, depending on coverage limits.""",
        "topics": ["3"],
        "summary": "Customer interested in legal protection insurance due to contractor disputes. Agent explains coverage for future disputes only and provides cost estimates."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Keller. Ich bin wirklich sauer auf die Schadensregulierung.
<agent>: Guten Tag Frau Keller, hier ist Luca Steiner. Es tut mir leid, dass Sie verärgert sind. Was ist geschehen?
<customer>: Glasschaden am Auto, Referenz SV-9922-T7. Der Schaden wurde abgelehnt wegen angeblicher Manipulation.
<agent>: Das ist ein schwerwiegender Vorwurf. Lassen Sie mich den Fall genau prüfen.
<customer>: Ich habe einen Steinschlag gehabt, das ist alles! Warum sollte ich das manipulieren?
<agent>: Ich verstehe Ihre Verärgerung. Können Sie mir den Hergang nochmals schildern?
<customer>: Ich fuhr hinter einem Lastwagen, plötzlich Knall in der Scheibe. Ganz normal halt.
<agent>: Haben Sie Zeugen oder war jemand anders im Auto?
<customer>: Meine Nachbarin sass neben mir. Sie kann das bestätigen.
<agent>: Das ist wichtig. Ich lasse den Fall von einem anderen Sachbearbeiter neu bewerten und berücksichtige die Zeugenaussage.
<customer>: Endlich jemand, der mir glaubt! Wann höre ich etwas?""",
        "topics": ["4"],
        "summary": "Customer angry about glass damage claim rejection due to alleged manipulation. Agent reopens case with new adjuster and includes witness testimony."
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Mitchell. I'm calling about my claim status.
<agent>: Hello Mr. Mitchell, this is Anna Meier from Vaudoise. What's your claim reference?
<customer>: SN-4433-L6. It's for water damage from a burst pipe last month.
<agent>: Let me check your file... I see the restoration work has been completed and final invoices received.
<customer>: Yes, everything's done. When can I expect final payment?
<agent>: The final payment has been approved and will be transferred to your account tomorrow morning.
<customer>: Excellent. Will there be any adjustment to the original estimate?
<agent>: Actually yes, the final amount is about 800 francs less than estimated because some damaged items could be repaired instead of replaced.
<customer>: That's good news. Will I receive a detailed final statement?
<agent>: Yes, you'll get a complete breakdown of all costs and payments by email today.
<customer>: Perfect. Thank you for the efficient handling of this claim.""",
        "topics": ["5"],
        "summary": "Customer receives positive update on water damage claim. Final payment approved with costs lower than estimated due to successful repairs rather than replacements."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Graf. Ich verstehe meine Prämienrechnung nicht.
<agent>: Guten Tag Herr Graf, hier ist Pascal Tremblay. Was ist unklar an Ihrer Rechnung?
<customer>: Es gibt verschiedene Abzüge und Zuschläge, ich kenne mich nicht aus.
<agent>: Gerne erkläre ich Ihnen die Rechnung Schritt für Schritt. Haben Sie sie vor sich?
<customer>: Ja. Da steht etwas von einem Schadenfreiheitsrabatt und einem Selbstbehalt-Bonus.
<agent>: Der Schadenfreiheitsrabatt belohnt Sie dafür, dass Sie keine Schäden hatten. Je länger schadensfrei, desto höher der Rabatt.
<customer>: Und der Selbstbehalt-Bonus?
<agent>: Den erhalten Sie, weil Sie einen höheren Selbstbehalt gewählt haben. Das reduziert Ihre Grundprämie.
<customer>: Verstehe. Und warum ist dann noch ein Zuschlag da?
<agent>: Welcher Zuschlag genau? Können Sie mir die Zeile vorlesen?
<customer>: "Regionale Anpassung +15%".
<agent>: Das ist ein regionaler Zuschlag aufgrund höherer Schadenkosten in Ihrer Gegend. Der ist leider unvermeidlich.""",
        "topics": ["6"],
        "summary": "Customer confused about premium calculation details. Agent explains no-claims discount, deductible bonus, and regional adjustment factors step by step."
    },
    {
        "transcript": """<customer>: Bonjour, ici Monsieur Leroy. J'ai des questions sur ma couverture santé.
<agent>: Bonjour Monsieur Leroy, ici Sarah Dürst. En quoi puis-je vous aider?
<customer>: Mon dentiste propose un nouveau traitement coûteux et je veux savoir ce qui est pris en charge.
<agent>: De quel type de traitement s'agit-il?
<customer>: Des implants dentaires. Cela coûte environ 8000 francs.
<agent>: Regardons votre police GS-6688-U7... Vous avez une couverture dentaire avec certaines limitations.
<customer>: Quelles limitations?
<agent>: Les implants sont couverts à hauteur de 75% maximum 5000 francs par an pour les traitements dentaires majeurs.
<customer>: Donc je recevrais 5000 francs maximum?
<agent>: Exactement. Et il faut d'abord obtenir une autorisation de coûts avant de commencer le traitement.
<customer>: Comment faire cette demande?
<agent>: Votre dentiste doit nous envoyer un plan de traitement détaillé avec devis. Nous évaluons ensuite la nécessité médicale.""",
        "topics": ["7"],
        "summary": "Customer asks about dental implant coverage. Policy covers 75% up to 5000 francs annually for major dental work with prior authorization required."
    },
    {
        "transcript": """<customer>: Good morning, this is Mrs. Cooper. I need emergency roadside assistance.
<agent>: Good morning Mrs. Cooper, this is Yann Morel from Vaudoise assistance. What's your emergency?
<customer>: My car battery is dead in a parking garage. I think I left the lights on overnight.
<agent>: That happens to everyone! Are you in a safe, accessible location for our service vehicle?
<customer>: Yes, it's a public parking garage with good access.
<customer>: Can you give me your exact location and policy number?
<agent>: I'm at the Westside shopping center in Bern, underground parking level 1. Policy PH-5577-N9.
<agent>: Perfect. I can dispatch a mobile battery service immediately. They'll have jump cables and replacement batteries if needed.
<customer>: How quickly can they get here?
<agent>: For parking garage locations, usually 15-20 minutes. They'll call you when they arrive at the entrance.
<customer>: Excellent service! Thank you for the quick response.""",
        "topics": ["8"],
        "summary": "Customer needs jump start for dead battery in shopping center parking garage. Mobile battery service dispatched with 15-20 minute response time."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Gross. Frage zur Gebäudeversicherung.
<agent>: Guten Tag Herr Gross, hier ist Marc Ducret. Womit kann ich helfen?
<customer>: Wir installieren eine Wärmepumpe. Ändert das etwas an der Versicherung?
<agent>: Eine Wärmepumpe ist eine wertvolle Gebäudeinstallation und sollte mitversichert werden.
<customer>: Die Anlage kostet 25.000 Franken. Um wie viel steigt die Prämie?
<agent>: Bei Ihrer Police HR-1199-X3 würde das etwa 60-80 Franken Mehrprämie pro Jahr bedeuten.
<customer>: Das ist moderat. Gibt es besondere Risiken bei Wärmepumpen?
<agent>: Hauptrisiken sind Frost-, Elektronik- und Vandalismusschäden. Letztere sind leider nicht selten.
<customer>: Vandalismusschäden? Bei einer Wärmepumpe?
<agent>: Ja, die Außengeräte werden leider manchmal mutwillig beschädigt. Deshalb ist eine umfassende Deckung wichtig.
<customer>: Dann sollten wir das auf jeden Fall machen. Schicken Sie mir die Unterlagen.""",
        "topics": ["9"],
        "summary": "Customer installing heat pump asks about building insurance implications. Agent explains coverage importance including vandalism protection for outdoor units."
    },
    {
        "transcript": """<customer>: Bonjour, ici Madame Vincent. Question sur mon assurance véhicule.
<agent>: Bonjour Madame Vincent, ici Luca Steiner de Vaudoise. Que voulez-vous savoir?
<customer>: Je vais acheter une voiture électrique. Est-ce que cela change quelque chose à mon assurance?
<agent>: Les voitures électriques ont quelques spécificités. Elles nécessitent souvent une couverture étendue pour la batterie.
<customer>: Pourquoi la batterie spécifiquement?
<agent>: Les batteries coûtent très cher à remplacer et ont des risques particuliers comme la surchauffe ou les dégâts dus au sel de route.
<customer>: Et pour l'assistance routière?
<agent>: Nous recommandons une assistance étendue car les pannes électriques nécessitent des dépanneurs spécialisés.
<customer>: Cela va coûter beaucoup plus cher?
<agent>: Environ 10-15% de plus qu'une voiture classique, mais c'est justifié par les technologies spécifiques.
<customer>: D'accord. Préparez-moi une offre complète pour véhicule électrique.""",
        "topics": ["10"],
        "summary": "Customer buying electric vehicle asks about insurance differences. Agent explains battery coverage and specialized roadside assistance needs with modest premium increase."
    },
    {
        "transcript": """<customer>: Good afternoon, this is Mr. Baker. I have a travel insurance inquiry.
<agent>: Good afternoon Mr. Baker, this is Anna Meier from Vaudoise. How can I help you?
<customer>: I'm planning a hiking trip in the Himalayas. Does my travel insurance cover high-altitude activities?
<agent>: That's an adventure! Let me check your policy RV-3399-H8... You have standard travel insurance which has altitude restrictions.
<customer>: What kind of restrictions?
<agent>: Standard coverage applies up to 4,500 meters altitude. Above that, you need specialized high-altitude coverage.
<customer>: The trek goes up to 5,500 meters. What are my options?
<agent>: We can arrange an extension for high-altitude activities, including helicopter evacuation if needed.
<customer>: Helicopter evacuation? That sounds expensive.
<agent>: It is, but essential at those altitudes where normal rescue isn't possible. The extension is about 200 francs for a two-week trip.
<customer>: That's reasonable for peace of mind. Please arrange the high-altitude coverage.""",
        "topics": ["11"],
        "summary": "Customer planning Himalayan trek needs high-altitude travel insurance extension above 4,500 meters. Coverage includes specialized evacuation services."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Schmid. Es geht um meine Lebensversicherung.
<agent>: Guten Tag Frau Schmid, hier ist Pascal Tremblay. Wie kann ich helfen?
<customer>: Mein Mann ist verstorben und ich muss die Leistung beantragen.
<agent>: Mein herzliches Beileid, Frau Schmid. Ich helfe Ihnen gerne bei allen Formalitäten.
<customer>: Welche Unterlagen brauchen Sie?
<agent>: Den Sterbeausweis, eine Kopie des Ehescheins und ein ausgefülltes Leistungsformular.
<customer>: Wie lange dauert die Bearbeitung normalerweise?
<agent>: Nach Eingang aller Unterlagen etwa 10-14 Tage. In besonderen Härtefällen können wir eine Vorauszahlung leisten.
<customer>: Das wäre hilfreich, da ich hohe Bestattungskosten habe.
<agent>: Das verstehe ich. Ich sende Ihnen alle Formulare und organisiere eine Vorauszahlung von 50% der Versicherungssumme.
<customer>: Vielen Dank für Ihr Verständnis und Ihre Hilfe.
<agent>: Das ist selbstverständlich in dieser schweren Zeit.""",
        "topics": ["12"],
        "summary": "Widow applies for life insurance benefits after husband's death. Agent offers compassionate processing with 50% advance payment to help with funeral costs."
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Taylor. I have a question about my valuables coverage.
<agent>: Hello Ms. Taylor, this is Sarah Dürst from Vaudoise. What would you like to know?
<customer>: I'm getting married and received expensive wedding gifts. How do I add them to my insurance?
<agent>: Congratulations on your wedding! New valuable items should be reported within 30 days of acquisition.
<customer>: What constitutes a valuable item that needs special coverage?
<agent>: Generally items worth more than 2,000 francs like jewelry, art, or collectibles should be individually listed.
<customer>: I received a diamond necklace and some silver pieces. Do I need appraisals?
<agent>: For items over 5,000 francs, we require professional appraisals. For others, purchase receipts or gift documentation suffice.
<customer>: The necklace is worth about 8,000 francs. Can you recommend an appraiser?
<agent>: Certainly, I'll send you a list of certified jewelry appraisers in your area along with the coverage update forms.""",
        "topics": ["13"],
        "summary": "Newlywed needs to add expensive wedding gifts to valuables coverage. Agent explains reporting requirements and appraisal needs for high-value items.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Wolf. Ich habe eine grundlegende Frage zu Versicherungen.
<agent>: Guten Tag Herr Wolf, hier ist Marc Ducret. Womit kann ich Ihnen helfen?
<customer>: Ich ziehe bald ins Ausland und frage mich, was mit meinen Schweizer Versicherungen passiert.
<agent>: Das hängt davon ab, ob es ein vorübergehender oder dauerhafter Umzug ist und wohin Sie gehen.
<customer>: Ich gehe für mindestens fünf Jahre nach Deutschland für einen Job.
<agent>: Bei einem längerfristigen Umzug nach Deutschland können die meisten Versicherungen nicht einfach fortgeführt werden.
<customer>: Auch nicht die Lebensversicherung?
<agent>: Lebensversicherungen können oft fortgeführt werden, aber Sachversicherungen wie Auto und Hausrat müssen normalerweise gekündigt werden.
<customer>: Was ist mit meinen Rabatten und der Schadenfreiheit?
<agent>: Die Schadenfreiheit können wir Ihnen bescheinigen für die Verwendung bei deutschen Versicherern.
<customer>: Das ist gut zu wissen. Können Sie mir eine komplette Übersicht machen?
<agent>: Sehr gerne. Ich erstelle Ihnen eine detaillierte Auswanderer-Checkliste für alle Ihre Policen.""",
        "topics": ["1"],
        "summary": "Customer moving to Germany for work asks about insurance implications. Agent explains different rules for life vs property insurance and offers emigration checklist."
    },
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
        "suggested_topics": ["1"],
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
        "suggested_topics": ["2"],
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
        "suggested_topics": ["2"],
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