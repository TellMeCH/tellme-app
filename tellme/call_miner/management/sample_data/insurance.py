TOPIC_DATA = [
    {
        "name": "General Enquiry",
        "description": "General questions or requests for information related to insurance services, policy coverage, or procedures."
    },
    {
        "name": "Unserved Insurance Need",
        "description": "Identifying insurance requirements that are not currently addressed by existing policies or coverage."
    },
    {
        "name": "Sales / Prospect Call",
        "description": "Interactions focused on selling insurance products or discussing services with potential new customers."
    },
    {
        "name": "Claim Negotiation",
        "description": "Discussions around the terms, amounts, or conditions of insurance claims, including disputes and settlements."
    },
    {
        "name": "Claim Follow-Up",
        "description": "Checking the status or progress of previously submitted insurance claims or related documents."
    },
    {
        "name": "Premiums and Payments",
        "description": "Inquiries regarding premium amounts, payment schedules, due dates, and payment methods for insurance policies."
    },
    {
        "name": "Healthcare Support",
        "description": "Requests for assistance or information about healthcare coverage, benefits, or provider networks."
    },
    {
        "name": "Roadside Support",
        "description": "Requests for emergency assistance or support related to vehicles, such as breakdowns or accidents."
    },
    {
        "name": "Property Insurance",
        "description": "Questions or support related to insurance coverage for homes, buildings, or other property assets."
    },
    {
        "name": "Vehicle Insurance",
        "description": "Discussions about vehicle insurance policies, coverage options, claims, and renewals."
    },
    {
        "name": "Travel Insurance",
        "description": "Inquiries and support regarding insurance coverage for travel, trips, cancellations, and emergencies."
    },
    {
        "name": "Life Insurance",
        "description": "Support and information about life insurance policies, beneficiaries, and claims."
    },
    {
        "name": "Valuable Items Insurance",
        "description": "Coverage options and claims support for high-value personal items such as jewelry, art, or collectibles."
    }
]
SUGGESTED_TOPIC_DATA = [
    {
        "name": "Insurance Extension",
        "description": "Requests or discussions about extending existing insurance coverage to include additional risks or longer periods."
    },
    {
        "name": "Coverage Adjustment",
        "description": "Inquiries about changing, increasing, or reducing coverage in an existing insurance policy."
    },
    {
        "name": "Discount Offer",
        "description": "Communication related to offering special pricing, loyalty discounts, or promotional rates for insurance products."
    },
    {
        "name": "Risk Assessment",
        "description": "Evaluation of a customer's risk profile to determine eligibility, premiums, or policy terms."
    },
    {
        "name": "Contract Renewal Reminder",
        "description": "Notifications or follow-up calls reminding customers to renew their insurance contracts before expiration."
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
        "transcript": """<customer>: Bonjour, ici Madame Dubois. J'ai un problème avec ma réclamation d'assurance auto.
<agent>: Bonjour Madame Dubois, ici Pierre-Alain Müller de Vaudoise. Comment puis-je vous aider?
<customer>: J'ai soumis ma réclamation il y a trois semaines mais je n'ai toujours pas de nouvelles.
<agent>: Je vais vérifier le statut de votre dossier. Pouvez-vous me donner votre numéro de police?
<customer>: C'est le 78-VH-2841-F2.
<agent>: Merci. Je vois que l'expert doit encore examiner les dégâts. L'évaluation est prévue pour demain.
<customer>: Enfin! Ma voiture est immobilisée depuis l'accident. Quand aurai-je une voiture de remplacement?
<agent>: Dès que l'expertise confirme que les réparations prendront plus de 48 heures, nous activons automatiquement le véhicule de remplacement.
<customer>: Et si la voiture est déclarée perte totale?
<agent>: Dans ce cas, nous calculons la valeur vénale et vous proposons un règlement dans les 5 jours ouvrables.
<customer>: D'accord. Pouvez-vous me tenir informée par SMS?
<agent>: Bien sûr, j'active les notifications SMS pour votre dossier.""",
        "topics": ["5", "10"],
        "summary": "Customer follows up on auto insurance claim submitted three weeks ago. Agent schedules expert evaluation and explains replacement vehicle and total loss procedures.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Kaufmann. Ich interessiere mich für eine Gewerbeversicherung.
<agent>: Guten Tag Herr Kaufmann, hier ist Anna Weber. Gerne berate ich Sie. Was für ein Gewerbe haben Sie?
<customer>: Ich eröffne bald eine kleine Bäckerei in Bern und brauche umfassenden Schutz.
<agent>: Eine Bäckerei hat spezielle Risiken. Wir brauchen Betriebshaftpflicht, Inventarschutz und Betriebsunterbrechung.
<customer>: Was kostet so ein Paket ungefähr?
<agent>: Das hängt von der Ladenfläche und dem Umsatz ab. Können Sie mir diese Angaben machen?
<customer>: 80 Quadratmeter Verkaufsfläche und ich rechne mit 300.000 Franken Jahresumsatz.
<agent>: Für diese Größenordnung liegen die Prämien bei etwa 2.500 bis 3.200 Franken jährlich.
<customer>: Sind Kundenunfälle auch abgedeckt?
<agent>: Ja, die Betriebshaftpflicht deckt Personen- und Sachschäden von Kunden in Ihrem Geschäft ab.
<customer>: Gut. Können Sie mir ein detailliertes Angebot erstellen?
<agent>: Sehr gerne. Ich erstelle Ihnen ein individuelles Angebot für alle relevanten Versicherungsbereiche.""",
        "topics": ["3", "9"],
        "summary": "Prospective bakery owner inquires about comprehensive business insurance coverage. Agent explains specific risks and provides pricing estimates for liability, inventory, and business interruption insurance.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Thompson. I need to file a claim for water damage in my apartment.
<agent>: Hello Mr. Thompson, this is Julia Zimmermann from Vaudoise. I'm sorry to hear about the damage. Can you tell me what happened?
<customer>: A pipe burst in the wall behind my bathroom and flooded my living room overnight.
<agent>: That sounds serious. Have you taken any immediate measures to prevent further damage?
<customer>: Yes, I turned off the main water supply and called a plumber. He's coming this afternoon.
<agent>: Perfect. Have you documented the damage with photos?
<customer>: I took about 20 photos showing the water damage to the floors and furniture.
<agent>: Excellent. For household insurance claims, we'll need those photos, a plumber's report, and an inventory of damaged items.
<customer>: My expensive Persian rug is completely ruined. Is that covered?
<agent>: Household contents are covered up to the policy limits. Do you have a purchase receipt for the rug?
<customer>: Yes, I bought it last year for 4,500 francs.
<agent>: With the receipt, it should be covered. I'll arrange for a claims adjuster to visit tomorrow morning.""",
        "topics": ["4", "9"],
        "summary": "Customer reports water damage from burst pipe flooding apartment. Agent guides through immediate steps and schedules claims adjuster visit for household insurance evaluation."
    },
    {
        "transcript": """<customer>: Bonjour, c'est Monsieur Bertrand. Ma prime d'assurance a augmenté de 30% cette année!
<agent>: Bonjour Monsieur Bertrand, ici Céline Rossier. Je comprends votre surprise. Laissez-moi vérifier votre dossier.
<customer>: L'année dernière je payais 1.200 francs, maintenant c'est 1.560 francs. C'est énorme!
<agent>: Je vois que vous avez eu deux sinistres l'année passée. Cela explique l'ajustement de prime.
<customer>: Mais ces accidents n'étaient pas ma faute! L'un était causé par la grêle.
<agent>: Les sinistres météo comptent aussi dans le calcul du risque, même sans responsabilité de votre part.
<customer>: C'est injuste. Y a-t-il un moyen de réduire cette augmentation?
<agent>: Nous pourrions augmenter votre franchise de 500 à 1.000 francs. Cela réduirait la prime d'environ 200 francs par an.
<customer>: Et si je n'ai plus de sinistres cette année?
<agent>: Après une année sans sinistre, vous récupérez progressivement vos bonus. La prime diminuera de 5% l'année prochaine.
<customer>: D'accord, augmentons la franchise. Quand cette modification prend-elle effet?
<agent>: La modification sera effective dès le prochain renouvellement en janvier.""",
        "topics": ["6", "10"],
        "summary": "Customer complains about 30% premium increase due to two previous claims. Agent explains risk calculation and offers franchise adjustment to reduce premium costs.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Keller. Ich brauche eine Auslandskrankenversicherung für meine Reise nach Thailand.
<agent>: Guten Tag Frau Keller, hier ist Thomas Meier. Wie lange dauert Ihre Reise und was für Aktivitäten sind geplant?
<customer>: Drei Wochen im März. Hauptsächlich Strandurlaub, aber auch eine mehrtägige Dschungeltour.
<agent>: Für Thailand empfehle ich unsere Premium-Reiseversicherung mit erhöhter Deckung für Tropenkrankheiten.
<customer>: Welche medizinischen Kosten sind abgedeckt?
<agent>: Bis zu 500.000 Franken für Behandlung und Spitalkosten, plus Rücktransport in die Schweiz falls nötig.
<customer>: Was ist mit den Dschungeltouren? Sind Abenteueraktivitäten versichert?
<agent>: Grundsätzlich ja, aber extreme Sportarten wie Fallschirmspringen sind ausgeschlossen. Trekking ist abgedeckt.
<customer>: Gut. Was kostet die Versicherung für drei Wochen?
<agent>: Für Thailand beträgt die Prämie 95 Francs für drei Wochen mit Vollschutz.
<customer>: Das ist vernünftig. Kann ich sie online abschließen?
<agent>: Ja, oder ich kann sie für Sie aktivieren. Sie erhalten dann alle Dokumente per E-Mail.""",
        "topics": ["11", "7"],
        "summary": "Customer needs travel insurance for three-week Thailand trip including jungle tours. Agent recommends premium coverage for tropical diseases and adventure activities.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. Garcia. I'm calling about my life insurance policy.
<agent>: Hello Mrs. Garcia, this is David Studer from Vaudoise. How may I help you today?
<customer>: I want to increase my coverage amount. My current policy is for 100,000 francs but I think I need more.
<agent>: I understand. Have there been changes in your financial situation that require higher coverage?
<customer>: Yes, we bought a house and have a mortgage of 400,000 francs. My husband would need more protection.
<agent>: That makes sense. Increasing coverage usually requires a health assessment. Are you in good health?
<customer>: Yes, I'm healthy. I exercise regularly and have no medical issues.
<agent>: Excellent. For increases up to 200,000 francs, we only need a health questionnaire. Above that requires medical exams.
<customer>: I was thinking of 300,000 total coverage. What would that cost?
<agent>: At your age of 32, the additional 200,000 francs would cost approximately 180 francs annually.
<customer>: That's reasonable for the peace of mind. How long does the approval process take?
<agent>: With medical exams, typically 4-6 weeks. I can schedule your appointment and send the forms today.""",
        "topics": ["12", "3"],
        "summary": "Customer wants to increase life insurance from 100,000 to 300,000 francs due to new mortgage. Agent explains health assessment requirements and pricing for coverage increase."
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Herr Widmer. Mein Motorrad wurde gestohlen und ich möchte eine Schadensmeldung machen.
<agent>: Guten Tag Herr Widmer, hier ist Sandra Bühler. Tut mir leid zu hören. Wann ist der Diebstahl passiert?
<customer>: Gestern Abend zwischen 18 und 22 Uhr. Es war vor meiner Wohnung parkiert.
<agent>: Haben Sie bereits Anzeige bei der Polizei erstattet?
<customer>: Ja, heute Morgen. Hier ist die Anzeigenummer: BE-2024-15784.
<agent>: Perfekt. Welches Motorrad war es und wie war es gesichert?
<customer>: Eine Yamaha MT-09 von 2022, schwarz. Ich hatte ein Lenkradschloss und eine Kette durch das Hinterrad.
<agent>: War es an einem festen Gegenstand angekettet?
<customer>: Ja, an einem Metallpfosten. Aber die haben die Kette durchgeschnitten.
<agent>: Bei professionellem Diebstahl trotz Sicherung ist die Vollkasko zur Deckung verpflichtet. Haben Sie den Kaufbeleg?
<customer>: Ja, ich habe alle Originalunterlagen. Das Motorrad kostete 12.500 Franken.
<agent>: Dann rechnen wir mit dem Zeitwert von etwa 10.500 Franken. Die Auszahlung erfolgt nach Abschluss der Polizeiermittlungen.
<customer>: Wie lange dauert das normalerweise?
<agent>: Meist 2-3 Wochen. Falls das Motorrad nicht auftaucht, erhalten Sie dann die Entschädigung.""",
        "topics": ["4", "10"],
        "summary": "Customer reports motorcycle theft with proper security measures. Agent confirms full insurance coverage and explains settlement process after police investigation.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Roux. Je pars en retraite et je me demande ce qui arrive à mes assurances.
<agent>: Bonjour Madame Roux, ici Laurent Perrin. Félicitations pour votre retraite! Quelles assurances vous préoccupent?
<customer>: Principalement l'assurance maladie complémentaire et ma voiture. Vais-je payer moins cher?
<agent>: Pour l'assurance maladie, les primes restent les mêmes. Mais pour l'auto, vous pourriez bénéficier de rabais retraité.
<customer>: Un rabais retraité? Comment ça fonctionne?
<agent>: Si vous roulez moins de 10.000 km par an, nous offrons 15% de réduction sur la responsabilité civile.
<customer>: C'est intéressant! Je ne roule plus que 6.000 km par an maintenant.
<agent>: Parfait. Nous pourrions aussi adapter votre couverture casco si vous utilisez moins la voiture.
<customer>: Mon auto a maintenant 8 ans. Vaut-elle encore la peine d'être assurée casco complète?
<agent>: Avec une valeur de moins de 8.000 francs, une demi-casco pourrait suffire et vous économiserait 300-400 francs par an.
<customer>: Cela semble logique. Pouvez-vous calculer les économies totales?
<agent>: Avec le rabais retraité et la demi-casco, vous économiseriez environ 520 francs annuellement.""",
        "topics": ["6", "10"],
        "summary": "Retired customer inquires about insurance adjustments. Agent explains retirement discounts for reduced driving and recommends switching to partial coverage to save money.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Anderson. I need roadside assistance for my car.
<agent>: Hello Mr. Anderson, this is Monica Käser from Vaudoise roadside service. Where is your location?
<customer>: I'm on the A1 highway between Bern and Zurich, about 20 kilometers from Bern.
<agent>: What seems to be the problem with your vehicle?
<customer>: The engine overheated and now it won't start. There's steam coming from under the hood.
<agent>: Please move to a safe location if possible and turn on your hazard lights. Do not open the hood while it's hot.
<customer>: I'm already on the shoulder with hazards on. How long will it take for help to arrive?
<agent>: I'm dispatching a service vehicle now. Estimated arrival time is 25-30 minutes.
<customer>: Will you be able to fix it on the spot or do I need towing?
<agent>: Engine overheating often requires towing to a garage for proper diagnosis and repair.
<customer>: I have a meeting in Zurich this afternoon. Can you arrange a rental car?
<agent>: Yes, if towing is necessary, we can provide a replacement vehicle. The service technician will assess and arrange everything.
<customer>: Great, thank you. Should I stay in the car?
<agent>: For safety on the highway, please wait outside the vehicle but behind the barrier if there is one.""",
        "topics": ["8", "10"],
        "summary": "Customer requests roadside assistance for overheated engine on highway. Agent dispatches service vehicle and explains safety procedures and replacement car options."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Schneider. Ich habe Fragen zu meiner Prämienrechnung.
<agent>: Guten Tag Frau Schneider, hier ist Roberto Silva. Womit kann ich Ihnen helfen?
<customer>: Meine Hausratversicherung ist um 80 Franken gestiegen, aber ich verstehe nicht warum.
<agent>: Lassen Sie mich Ihr Dossier prüfen. Haben Sie kürzlich Änderungen an Ihrer Wohnsituation gemeldet?
<customer>: Ja, ich bin in eine größere Wohnung umgezogen. Aber 80 Franken Aufschlag scheint mir viel.
<agent>: Der Umzug von 2.5 auf 4.5 Zimmer bedeutet höhere Versicherungssummen für Hausrat und erhöhtes Einbruchrisiko.
<customer>: Das Einbruchrisiko? Ich wohne jetzt sogar in einem sichereren Quartier.
<agent>: Das stimmt, aber Erdgeschosswohnungen haben grundsätzlich einen Risikozuschlag von 50 Franken.
<customer>: Ach so, ich wohne jetzt ebenerdig. Das wusste ich nicht.
<agent>: Die restlichen 30 Franken kommen durch die höhere Versicherungssumme für den größeren Hausrat.
<customer>: Kann ich etwas machen, um die Prämie zu senken?
<agent>: Mit Sicherheitsmaßnahmen wie Alarmanlagen oder verstärkten Türen erhalten Sie Rabatte.
<customer>: Meine neue Wohnung hat bereits eine Alarmanlage. Zählt das?
<agent>: Definitiv! Mit einer zertifizierten Alarmanlage reduziert sich die Prämie um 25 Franken jährlich.""",
        "topics": ["6", "9"],
        "summary": "Customer questions household insurance premium increase after moving to larger ground floor apartment. Agent explains risk factors and offers security system discount.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Monsieur Favre. Je vais acheter une nouvelle voiture et j'aimerais transférer mon assurance.
<agent>: Bonjour Monsieur Favre, ici Nathalie Steiner. Félicitations pour votre nouvelle voiture! De quel modèle s'agit-il?
<customer>: Je remplace ma Honda Civic par une Tesla Model 3. Est-ce que ça change beaucoup pour l'assurance?
<agent>: Les voitures électriques ont parfois des primes différentes. Quelle est la valeur de la Tesla?
<customer>: 65.000 francs, neuve. Mon ancienne voiture valait 15.000 francs.
<agent>: Avec cette valeur plus élevée, la casco complète coûtera plus cher. Environ 300 francs supplémentaires par année.
<customer>: C'est raisonnable. Y a-t-il des avantages pour les voitures électriques?
<agent>: Oui, nous offrons 10% de réduction sur la responsabilité civile pour les véhicules électriques.
<customer>: Parfait! Quand puis-je faire le changement?
<agent>: Dès que vous avez les papiers d'immatriculation, nous activons l'assurance pour la Tesla.
<customer>: Et pour mon bonus-malus, ça reste pareil?
<agent>: Absolument, vos années sans sinistre sont transférées automatiquement sur le nouveau véhicule.
<customer>: Excellent. J'aurai les papiers vendredi. Pouvez-vous préparer le dossier?
<agent>: Bien sûr, je prépare tout et vous contacte vendredi pour finaliser le transfert.""",
        "topics": ["10", "3"],
        "summary": "Customer wants to transfer car insurance to new Tesla replacing older Honda. Agent explains premium changes for electric vehicle and confirms bonus transfer process.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Johnson. I'm concerned about my health insurance coverage.
<agent>: Hello Ms. Johnson, this is Patrick Müller from Vaudoise. What specific concerns do you have?
<customer>: I need surgery for a knee replacement and want to make sure it's properly covered.
<agent>: Orthopedic surgery is generally well covered. Do you have our basic or premium health plan?
<customer>: I have the premium plan with private room coverage. Will the surgery be fully covered?
<agent>: With premium coverage, you'll have choice of surgeon and private accommodation. There may be a small deductible.
<customer>: What about physiotherapy after the surgery? That could take months.
<agent>: Post-surgical physiotherapy is covered up to 36 sessions per year when medically prescribed.
<customer>: My doctor mentioned possible complications might require additional procedures.
<agent>: Any medically necessary follow-up treatments are covered under the same policy terms.
<customer>: Should I get pre-authorization before scheduling the surgery?
<agent>: Yes, for elective surgeries over 2,000 francs, we require pre-authorization to confirm coverage.
<customer>: How long does the authorization process take?
<agent>: Usually 5-7 business days once we receive the medical reports from your doctor.""",
        "topics": ["7", "1"],
        "summary": "Customer confirms health insurance coverage for knee replacement surgery. Agent explains premium plan benefits and pre-authorization requirements for elective procedures."
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Amstutz. Ich möchte meine Lebensversicherung kündigen.
<agent>: Guten Tag Herr Amstutz, hier ist Carla Bianchi. Darf ich fragen, warum Sie die Police kündigen möchten?
<customer>: Ich habe finanzielle Schwierigkeiten und brauche das Geld aus der Police.
<agent>: Das verstehe ich. Haben Sie schon über Alternativen zur Kündigung nachgedacht?
<customer>: Welche Alternativen gibt es denn?
<agent>: Sie könnten die Police beitragsfrei stellen oder ein Policendarlehen aufnehmen.
<customer>: Was bedeutet beitragsfrei stellen?
<agent>: Sie zahlen keine Prämien mehr, aber der Vertrag läuft weiter mit reduzierter Versicherungssumme.
<customer>: Und ein Policendarlehen?
<agent>: Sie können bis zu 80% des Rückkaufswertes als Darlehen beziehen und später zurückzahlen.
<customer>: Was wäre bei meiner Police möglich? Sie läuft seit 8 Jahren.
<agent>: Bei einem Rückkaufswert von 24.000 Franken könnten Sie 19.000 Franken als Darlehen erhalten.
<customer>: Das klingt interessanter als eine Kündigung. Welche Zinsen fallen an?
<agent>: Der Darlehenszins beträgt derzeit 2,5% pro Jahr, deutlich günstiger als Bankkredite.""",
        "topics": ["12", "6"],
        "summary": "Customer wants to cancel life insurance due to financial difficulties. Agent explains alternatives like premium-free continuation and policy loans to avoid cancellation.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Martin. J'ai eu un accident avec ma voiture et j'aimerais savoir comment procéder.
<agent>: Bonjour Madame Martin, ici François Dubois. J'espère que vous n'êtes pas blessée. Pouvez-vous me décrire l'accident?
<customer>: Non, je vais bien merci. J'ai reculé dans un parking et heurté une autre voiture.
<agent>: Avez-vous échangé les informations avec l'autre conducteur?
<customer>: Oui, nous avons rempli un constat amiable ensemble. L'autre voiture a quelques rayures sur le pare-chocs.
<agent>: Parfait. Qui était responsable selon le constat?
<customer>: J'ai accepté la responsabilité puisque je reculais. C'est clairement ma faute.
<agent>: Avec votre casco complète, vos dégâts sont couverts moins la franchise. Avez-vous pris des photos?
<customer>: Oui, j'ai photographié les deux véhicules sous tous les angles.
<agent>: Excellent. Pour ma voiture, l'aile arrière est enfoncée. Ça va coûter cher à réparer?
<agent>: Je ne peux pas estimer sans voir, mais notre réseau de garages partenaires vous fera un devis gratuit.
<customer>: Mon bonus va-t-il être affecté par cet accident?
<agent>: Malheureusement oui, avec un sinistre responsable vous perdrez deux degrés de bonus.""",
        "topics": ["4", "10"],
        "summary": "Customer reports parking lot accident where she was at fault. Agent explains comprehensive coverage, claims process and impact on no-claims bonus.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Roberts. I'm planning a motorcycle trip across Europe and need travel insurance.
<agent>: Hello Mr. Roberts, this is Elena Martinez from Vaudoise. That sounds exciting! Which countries will you be visiting?
<customer>: Germany, Austria, Italy, France, and Spain. The trip will last about three weeks.
<agent>: Motorcycle travel requires specific coverage. Do you have experience with long-distance motorcycle touring?
<customer>: Yes, I'm an experienced rider. I'm mainly concerned about medical coverage and motorcycle breakdown.
<agent>: Our travel insurance covers medical expenses up to 1 million francs, plus motorcycle repatriation if needed.
<customer>: What about theft or damage to my motorcycle while parked?
<agent>: We can add motorcycle coverage for theft and damage, but it requires additional premium.
<customer>: How much extra would that cost for a 15,000 franc motorcycle?
<agent>: Motorcycle coverage would add about 120 francs to the basic 180 franc travel premium.
<customer>: That's reasonable. What about coverage for my riding gear?
<agent>: Personal belongings including riding equipment are covered up to 3,000 francs.
<customer>: Perfect. Can you arrange everything for departure next Monday?
<agent>: Absolutely, I'll set up comprehensive motorcycle travel coverage starting Monday.""",
        "topics": ["11", "10"],
        "summary": "Customer needs travel insurance for three-week European motorcycle tour. Agent provides comprehensive coverage including medical, motorcycle protection, and equipment coverage.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Weber. Meine Hausratversicherung läuft bald ab und ich überdenke meine Deckung.
<agent>: Guten Tag Frau Weber, hier ist Marco Frei. Gerne schauen wir uns Ihre Bedürfnisse an. Was beschäftigt Sie?
<customer>: Ich habe in den letzten Jahren viele neue Möbel gekauft und frage mich, ob die Versicherungssumme noch ausreicht.
<agent>: Das ist eine wichtige Überlegung. Wie hoch ist Ihre aktuelle Versicherungssumme?
<customer>: 80.000 Franken. Aber allein meine neue Küche hat 25.000 Franken gekostet.
<agent>: Mit neuen Möbeln sollten wir die Summe anpassen. Haben Sie eine Schätzung des Gesamtwerts?
<customer>: Ich denke, alles zusammen ist mindestens 120.000 Franken wert.
<agent>: Dann empfehle ich eine Erhöhung auf 130.000 Franken als Sicherheitspuffer.
<customer>: Um wie viel steigt dann die Prämie?
<agent>: Die Erhöhung von 50.000 Franken kostet etwa 85 Franken mehr pro Jahr.
<customer>: Das ist verkraftbar. Sind teure Einzelstücke automatisch mitversichert?
<agent>: Gegenstände über 5.000 Franken sollten separat deklariert werden für vollen Schutz.
<customer>: Mein neuer Esstisch kostete 8.000 Franken. Muss ich den melden?
<agent>: Ja, für optimalen Schutz sollten wir den als Einzelstück auflisten.""",
        "topics": ["9", "1"],
        "summary": "Customer reviews household insurance coverage due to expensive new furniture purchases. Agent recommends increasing sum insured and declaring high-value individual items.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Monsieur Leclerc. Je viens d'acheter une maison et j'ai besoin d'une assurance bâtiment.
<agent>: Bonjour Monsieur Leclerc, ici Sylvie Rochat. Félicitations pour votre acquisition! Pouvez-vous me décrire la propriété?
<customer>: C'est une maison de 1985, 5.5 pièces, avec garage attenant. Elle a été rénovée en 2018.
<agent>: Quelle est la valeur de reconstruction estimée selon l'expertise?
<customer>: L'expert a estimé 850.000 francs pour une reconstruction complète.
<agent>: Avec les rénovations récentes, nous pourrions même recommander 900.000 francs comme valeur d'assurance.
<customer>: Pourquoi plus que l'estimation?
<agent>: Les coûts de construction augmentent constamment. Un surplus protège contre l'inflation des prix.
<customer>: Cela semble prudent. Quels risques sont couverts?
<agent>: Incendie, dégâts d'eau, tempête, grêle, et optionnellement tremblement de terre et événements naturels.
<customer>: La région a déjà subi des inondations. Les événements naturels sont-ils recommandés?
<agent>: Absolument, surtout dans votre région. Cette couverture coûte environ 200 francs supplémentaires annuellement.
<customer>: Et pour le tremblement de terre?
<agent>: C'est plus rare mais les dégâts peuvent être catastrophiques. 150 francs de plus pour cette couverture.""",
        "topics": ["9", "3"],
        "summary": "Customer needs building insurance for newly purchased renovated house. Agent recommends adequate reconstruction value and additional coverage for natural disasters.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. Kim. I'm calling about my daughter's health insurance coverage while she studies abroad.
<agent>: Hello Mrs. Kim, this is Rachel Zimmermann from Vaudoise. Where will your daughter be studying?
<customer>: She's starting a master's degree in the United States that will last two years.
<agent>: US healthcare costs are extremely high. She'll need comprehensive international student coverage.
<customer>: Her university offers health insurance, but I want to make sure it's adequate.
<agent>: University plans often have limited coverage. Our international student policy provides unlimited medical coverage.
<customer>: What about emergency evacuation back to Switzerland?
<agent>: Our policy includes emergency repatriation up to 1 million francs if medically necessary.
<customer>: She has some ongoing medical conditions that require regular monitoring.
<agent>: Pre-existing conditions are covered after a 6-month waiting period with continuous coverage.
<customer>: The premium seems expensive at 2,400 francs per year. Is it worth it?
<agent>: In the US, a single emergency room visit can cost 10,000-50,000 francs. The premium is a small price for peace of mind.
<customer>: You're right. Can coverage start before she leaves Switzerland?
<agent>: Yes, we recommend activating coverage 2 weeks before departure to ensure seamless protection.""",
        "topics": ["7", "11"],
        "summary": "Mother seeks health insurance for daughter studying in US for two years. Agent explains comprehensive international coverage including pre-existing conditions and emergency repatriation."
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Herr Zürcher. Ich hatte einen Einbruch in meine Wohnung.
<agent>: Guten Tag Herr Zürcher, hier ist Linda Moser. Das tut mir sehr leid zu hören. Sind Sie unverletzt?
<customer>: Zum Glück war niemand zu Hause. Aber sie haben einiges gestohlen.
<agent>: Haben Sie bereits Anzeige bei der Polizei erstattet?
<customer>: Ja, heute Morgen. Die Spurensicherung war auch schon da.
<agent>: Gut. Können Sie mir sagen, was gestohlen wurde?
<customer>: Laptop, Tablet, Schmuck meiner Frau und etwa 500 Franken Bargeld.
<agent>: Haben Sie Belege für die gestohlenen Gegenstände?
<customer>: Für die Elektronik ja, aber für den Schmuck nur teilweise. Einige Stücke waren Erbstücke.
<agent>: Erbstücke sind schwieriger zu bewerten. Gibt es Fotos oder Schätzungen?
<customer>: Wir haben Fotos vom letzten Versicherungsupdate vor drei Jahren.
<agent>: Das hilft sehr. Wurde etwas beschädigt oder nur gestohlen?
<customer>: Sie haben Schränke durchwühlt und eine Tür aufgebrochen. Die Reparatur kostet etwa 800 Franken.
<agent>: Reparaturkosten sind auch gedeckt. Ich schicke Ihnen das Schadenformular und wir regeln alles weitere.
<customer>: Wie lange dauert die Bearbeitung normalerweise?
<agent>: Bei klaren Fällen wie Ihrem meist 2-3 Wochen nach Eingang aller Unterlagen.""",
        "topics": ["4", "9"],
        "summary": "Customer reports burglary with stolen electronics, jewelry and cash. Agent guides through claims process and explains coverage for both stolen items and property damage."
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Rousseau. Je souhaite assurer ma collection d'art.
<agent>: Bonjour Madame Rousseau, ici Antoine Perret. C'est un domaine spécialisé. Quel type d'œuvres possédez-vous?
<customer>: Principalement des peintures du 20ème siècle et quelques sculptures. La collection vaut environ 200.000 francs.
<agent>: Pour des objets d'art de cette valeur, il faut une police spécialisée avec expertises régulières.
<customer>: Que couvre exactement une assurance objets d'art?
<agent>: Vol, dégâts accidentels, incendie, dégâts d'eau, et même dépréciation due aux dommages.
<customer>: Et pour le transport? Je prête parfois mes œuvres pour des expositions.
<agent>: Le transport et les expositions peuvent être couverts moyennant supplément de prime.
<customer>: Les œuvres sont actuellement dans mon appartement. Est-ce suffisamment sécurisé?
<agent>: Nous exigeons certaines mesures de sécurité: alarme, détecteurs de fumée, serrures renforcées.
<customer>: J'ai une alarme mais pas de détecteurs spéciaux. Que recommandez-vous?
<agent>: Des détecteurs de fumée et d'eau sont essentiels. Un coffre-fort pour les petites pièces est aussi recommandé.
<customer>: Quel serait le coût annuel pour assurer ma collection?
<agent>: Pour 200.000 francs d'objets d'art, comptez environ 800-1.200 francs selon les mesures de sécurité.""",
        "topics": ["13", "3"],
        "summary": "Customer wants to insure 200,000 franc art collection. Agent explains specialized coverage requirements, security measures, and transport protection options.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Foster. I need to update my auto insurance because I'm buying a second car.
<agent>: Hello Mr. Foster, this is Benjamin Weber from Vaudoise. Congratulations on the new vehicle! What type of car are you adding?
<customer>: A used BMW from 2019. I want to keep my current car too, so I'll have two vehicles.
<agent>: With multiple vehicles, we can offer a multi-car discount. What's the value of the BMW?
<customer>: About 28,000 francs. It's mainly for weekend use and longer trips.
<agent>: For a second vehicle with limited use, you might want reduced coverage to save on premiums.
<customer>: What kind of reduced coverage do you recommend?
<agent>: We could do full liability but only partial comprehensive coverage since it's not your daily driver.
<customer>: How much would I save compared to full coverage?
<agent>: Approximately 400-500 francs annually, plus you get 10% multi-car discount on both vehicles.
<customer>: That sounds good. What about if I want to switch between the cars?
<agent>: With our flexible policy, you can transfer full coverage between vehicles with just a phone call.
<customer>: Perfect. How do we set this up?
<agent>: I'll prepare the multi-car policy with reduced coverage on the BMW and send you the details to review.""",
        "topics": ["10", "3"],
        "summary": "Customer adding second BMW to insurance policy. Agent explains multi-car discounts and flexible coverage options for weekend-use vehicle to optimize costs.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Huber. Ich möchte meine Reiseversicherung für eine Safari in Kenia erweitern.
<agent>: Guten Tag Frau Huber, hier ist Diana Steiner. Eine Safari ist ein tolles Erlebnis! Was für Aktivitäten sind geplant?
<customer>: Hauptsächlich Pirschfahrten und eine mehrtägige Wanderung in der Masai Mara.
<agent>: Für Kenia empfehlen wir erweiterte Tropenschutz-Deckung wegen Malaria und anderen Krankheiten.
<customer>: Ist eine Wanderung in der Wildnis als Extremsport eingestuft?
<agent>: Geführte Wanderungen mit professionellen Guides sind normalerweise abgedeckt.
<customer>: Was ist mit medizinischen Transporten? Die Gegend ist sehr abgelegen.
<agent>: Notfallevakuation per Flugzeug oder Helikopter ist bis 500.000 Franken gedeckt.
<customer>: Meine Kameraausrüstung ist 8.000 Franken wert. Ist das versichert?
<agent>: Wertgegenstände bis 3.000 Franken sind standard gedeckt. Für 8.000 Franken brauchen Sie eine Zusatzdeckung.
<customer>: Was kostet die Zusatzdeckung für die Kamera?
<agent>: Etwa 80 Franken für zwei Wochen, aber dann ist die komplette Ausrüstung gegen Diebstahl und Schäden versichert.
<customer>: Das nehme ich. Wie schnell kann die Deckung aktiviert werden?
<agent>: Sofort nach Vertragsabschluss. Soll ich alles für Sie vorbereiten?""",
        "topics": ["11", "13"],
        "summary": "Customer needs enhanced travel insurance for Kenya safari including tropical disease coverage and protection for expensive camera equipment. Agent arranges comprehensive coverage.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Monsieur Blanc. J'aimerais renégocier mes primes d'assurance.
<agent>: Bonjour Monsieur Blanc, ici Valérie Tschumi. Qu'est-ce qui vous amène à vouloir renégocier?
<customer>: J'ai reçu des offres de concurrents qui sont 20% moins chères que mes primes actuelles.
<agent>: Je comprends votre préoccupation. Puis-je voir quelles assurances vous avez chez nous?
<customer>: Auto, habitation et responsabilité civile. Au total je paie 2.800 francs par année.
<agent>: Depuis combien de temps êtes-vous client chez Vaudoise?
<customer>: 12 ans, sans aucun sinistre. C'est pour cela que ces offres m'intéressent.
<agent>: Votre fidélité mérite reconnaissance. Laissez-moi voir ce que je peux faire.
<customer>: Les concurrents offrent exactement la même couverture pour 2.240 francs.
<agent>: Je peux vous proposer un rabais fidélité de 15% qui ramènerait votre prime à 2.380 francs.
<customer>: C'est mieux mais encore 140 francs plus cher que la concurrence.
<agent>: Chez nous vous avez un service personnalisé et un règlement rapide des sinistres. Cela vaut quelque chose.
<customer>: C'est vrai, j'ai toujours été satisfait du service. 2.300 francs serait acceptable.
<agent>: D'accord pour 2.300 francs avec notre rabais grand client. Votre fidélité est importante pour nous.""",
        "topics": ["6", "1"],
        "summary": "Long-term customer wants to renegotiate premiums after receiving cheaper competitor offers. Agent provides loyalty discount to retain customer with competitive pricing.",
        "suggested_topics": ["3"]
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Chen. I'm a freelance consultant and need professional liability insurance.
<agent>: Hello Ms. Chen, this is Oliver Kaufmann from Vaudoise. What type of consulting do you do?
<customer>: I'm a financial consultant helping small businesses with accounting and tax planning.
<agent>: Financial consulting requires comprehensive professional liability coverage. What's your annual revenue?
<customer>: About 120,000 francs annually. I work with 15-20 clients per year.
<agent>: For financial services, we recommend coverage of at least 1 million francs for errors and omissions.
<customer>: What scenarios would be covered under professional liability?
<agent>: Incorrect advice leading to financial losses, missed deadlines, confidentiality breaches, and document errors.
<customer>: I'm worried about tax advice. If I make an error and the client gets audited, am I protected?
<agent>: Yes, professional liability covers defense costs and settlements from advice-related claims.
<customer>: What about cyber liability? I handle sensitive financial data.
<agent>: We can add cyber protection for data breaches and privacy violations. It's increasingly important for consultants.
<customer>: What would be the total premium for both coverages?
<agent>: For your revenue level, professional liability is about 800 francs and cyber coverage adds another 300 francs annually.
<customer>: That seems reasonable for the peace of mind. How quickly can coverage start?
<agent>: Coverage can be effective immediately upon completion of the application and payment.""",
        "topics": ["3", "1"],
        "summary": "Freelance financial consultant needs professional liability insurance. Agent explains comprehensive coverage for errors and omissions plus cyber protection for sensitive data.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Brunner. Ich habe Probleme mit der Schadensabwicklung meines Wasserschadens.
<agent>: Guten Tag Herr Brunner, hier ist Jasmin Hofstetter. Was für Probleme gibt es denn?
<customer>: Die Reparaturfirma sagt, sie müssen länger warten, weil der Experte noch nicht da war.
<agent>: Wann ist der Schaden denn passiert und wann war die Schadensmeldung?
<customer>: Der Rohrbruch war vor 10 Tagen und ich habe sofort angerufen. Seither passiert nichts.
<agent>: 10 Tage für eine Expertenbesichtigung ist definitiv zu lange. Lassen Sie mich das prüfen.
<customer>: Meine Küche ist unbenutzbar und das Parkett quillt auf. Es wird täglich schlimmer.
<agent>: Das verstehe ich. Bei Wasserschäden ist schnelles Handeln wichtig. Haben Sie die Trocknungsgeräte bekommen?
<customer>: Nein, mir wurde gesagt, ich müsse auf den Experten warten.
<agent>: Das ist falsch. Ich organisiere sofort Trocknungsgeräte und einen Nottermin mit unserem Experten.
<customer>: Endlich! Wann können die Geräte kommen?
<agent>: Noch heute Nachmittag. Der Experte kommt morgen früh und gibt die Reparatur frei.
<customer>: Was ist mit Mietminderung? Ich kann die Küche seit 10 Tagen nicht benutzen.
<agent>: Bei längeren Reparaturen übernehmen wir Zusatzkosten wie Außer-Haus-Essen während der Sperrung.""",
        "topics": ["5", "9"],
        "summary": "Customer frustrated with delayed water damage claim processing. Agent expedites expert visit and drying equipment, explains compensation for unusable kitchen.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Vuillard. Ma fille va commencer l'université et je me demande pour son assurance.
<agent>: Bonjour Madame Vuillard, ici Marc Tissot. Votre fille étudiera-t-elle chez vous ou ailleurs?
<customer>: Elle déménage à Lausanne pour ses études. Elle aura son propre appartement.
<agent>: Dans ce cas, elle a besoin de sa propre assurance ménage et responsabilité civile.
<customer>: Ne peut-elle pas rester sur ma police familiale?
<agent>: Jusqu'à 25 ans, elle peut rester couverte si elle vit chez vous. Sinon, il faut une police séparée.
<customer>: Combien coûte une assurance pour étudiante?
<agent>: Pour un studio d'étudiant, environ 150-200 francs par an pour ménage et responsabilité civile.
<customer>: Qu'est-ce qui est exactement couvert?
<agent>: Ses affaires personnelles, dommages qu'elle pourrait causer à autrui, et frais de logement si l'appartement devient inhabitable.
<customer>: Et pour les objets de valeur comme son ordinateur portable?
<agent>: Les appareils électroniques jusqu'à 2.000 francs sont automatiquement inclus.
<customer>: Elle a aussi une vélo électrique coûteux. Est-il assuré?
<agent>: Les vélos électriques jusqu'à 3.000 francs sont couverts contre vol et dommages.
<customer>: Parfait. Pouvez-vous préparer une offre pour quand elle déménage?
<agent>: Bien sûr, je prépare une police spéciale étudiante avec toutes les couvertures nécessaires.""",
        "topics": ["9", "3"],
        "summary": "Mother inquires about insurance for daughter starting university and moving to own apartment. Agent explains student-specific household and liability coverage options.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Peterson. I want to increase my life insurance coverage but I've been diagnosed with diabetes recently.
<agent>: Hello Mr. Peterson, this is Claudia Frei from Vaudoise. Thank you for disclosing your health condition. When were you diagnosed?
<customer>: Three months ago. My doctor says it's well-controlled with medication, but I'm worried about insurability.
<agent>: Type 2 diabetes that's well-managed doesn't automatically disqualify you, but it may affect pricing.
<customer>: I currently have 200,000 francs coverage and want to increase to 500,000 francs.
<agent>: For such a significant increase with a recent diagnosis, we'll need current medical reports.
<customer>: What specific tests or information do you need?
<agent>: Recent blood work showing glucose levels, HbA1c results, and a report from your treating physician.
<customer>: My last HbA1c was 6.8 and my doctor says that's good control. Will that help?
<agent>: Yes, HbA1c below 7.0 is considered good control and will work in your favor.
<customer>: How much might the premium increase due to diabetes?
<agent>: Well-controlled diabetes typically adds 25-50% to standard rates, depending on other health factors.
<customer>: That's reasonable for the extra protection. How long does underwriting take?
<agent>: With medical records, typically 3-4 weeks. I'll send you the forms and medical authorization today.""",
        "topics": ["12", "1"],
        "summary": "Customer with recent diabetes diagnosis wants to increase life insurance. Agent explains underwriting process for medical conditions and premium implications for well-controlled diabetes."
    },
    {
        "transcript": """<customer>: Guten Tag, hier spricht Frau Graf. Ich fahre bald in die Ferien und brauche eine Reiseversicherung.
<agent>: Guten Tag Frau Graf, hier ist Stefan Meier. Wohin geht die Reise und wie lange?
<customer>: Zwei Wochen nach Griechenland. Hauptsächlich Strandurlaub auf den Inseln.
<agent>: Griechenland ist EU, aber trotzdem empfehle ich eine Reiseversicherung für Notfälle und Rücktransport.
<customer>: Was kostet das für zwei Wochen Griechenland?
<agent>: Für zwei Personen etwa 65 Franken mit medizinischer Deckung und Annullierungsschutz.
<customer>: Annullierungsschutz? Was ist das genau?
<agent>: Falls Sie die Reise wegen Krankheit oder anderen versicherten Gründen absagen müssen, erstatten wir die Kosten.
<customer>: Mein Mann ist 68 Jahre alt und hat einen Herzschrittmacher. Ist er trotzdem versichert?
<agent>: Bestehende Gesundheitsprobleme sind versichert, solange sie stabil sind und keine Behandlungsänderung geplant ist.
<customer>: Er hatte letzten Monat eine Kontrolle und alles war in Ordnung.
<agent>: Das ist perfekt. Bei stabilen Vorerkrankungen gibt es keine Probleme mit der Deckung.
<customer>: Können wir auch Aktivitäten wie Schnorcheln machen?
<agent>: Schnorcheln ist als normaler Wassersport abgedeckt. Nur Gerätetauchen braucht Zusatzdeckung.
<customer>: Gut, dann nehmen wir das Komplettpaket. Wann ist es gültig?
<agent>: Ab sofort nach Vertragsabschluss, auch für Annullierungen vor der Reise.""",
        "topics": ["11"],
        "summary": "Customer needs travel insurance for two-week Greece vacation. Agent explains coverage for elderly spouse with pacemaker and includes cancellation protection.",
        "suggested_topics": ["5"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Monsieur Jaccard. J'ai reçu une mise en demeure de mon assureur auto pour non-paiement.
<agent>: Bonjour Monsieur Jaccard, ici Françoise Weber. Je vais regarder votre dossier immédiatement.
<customer>: Je pensais avoir payé toutes mes primes. Qu'est-ce qui se passe?
<agent>: Je vois qu'il manque le paiement du troisième trimestre qui était dû le 1er septembre.
<customer>: Septembre? Je pensais que c'était en octobre. N'ai-je pas reçu de rappel?
<agent>: Un premier rappel a été envoyé le 15 septembre, puis la mise en demeure le 1er octobre.
<customer>: Je n'ai rien reçu! Mon adresse a peut-être changé...
<agent>: Effectivement, nous avons encore l'ancienne adresse rue de la Paix. Quelle est la nouvelle?
<customer>: Avenue du Lac 15, 1005 Lausanne. J'ai déménagé en août mais j'ai oublié de vous le signaler.
<agent>: Cela explique tout. La mise en demeure est arrivée à l'ancienne adresse.
<customer>: Puis-je encore payer pour éviter la résiliation?
<agent>: Oui, vous avez encore 5 jours pour régulariser. Le montant dû est de 428 francs.
<customer>: Je paie immédiatement par e-banking. Pouvez-vous annuler la procédure?
<agent>: Dès réception du paiement, j'arrête la procédure et mets à jour votre adresse.""",
        "topics": ["6", "10"],
        "summary": "Customer receives payment demand for auto insurance due to missed payment caused by unreported address change. Agent helps resolve payment issue and updates address.",
        "suggested_topics": ["5"]
    },
    {
        "transcript": """<customer>: Hello, this is Mrs. O'Connor. I'm renovating my house and want to make sure I'm properly covered during construction.
<agent>: Hello Mrs. O'Connor, this is Andreas Moser from Vaudoise. What type of renovation work are you planning?
<customer>: We're adding a second story and completely remodeling the kitchen and bathrooms.
<agent>: Major renovations require special construction coverage. Your standard homeowner's policy may not be sufficient.
<customer>: What additional risks are there during construction?
<agent>: Fire hazards from equipment, theft of materials, liability for workers, and potential damage to existing structure.
<customer>: The contractor says he has insurance, but I want to make sure I'm protected too.
<agent>: Contractor insurance covers their liability, but you need coverage for the property and materials you own.
<customer>: How much will construction coverage cost for a six-month project?
<agent>: Typically 0.5% of the renovation value. For a 200,000 franc project, about 1,000 francs for six months.
<customer>: What happens if the renovation increases my home's value significantly?
<agent>: We'll need to update your policy limits once construction is complete to reflect the new replacement cost.
<customer>: Should I adjust my coverage now or wait until completion?
<agent>: I recommend temporary construction coverage now, then reassess full policy limits when work is finished.""",
        "topics": ["9", "1"],
        "summary": "Customer renovating house needs construction coverage for major addition and remodeling project. Agent explains additional risks and temporary coverage requirements.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Ritter. Mein Auto wurde bei einem Hagelschauer beschädigt.
<agent>: Guten Tag Herr Ritter, hier ist Corina Binder. Wo hat der Hagel Ihr Fahrzeug getroffen?
<customer>: Auf der A6 bei Thun. Es war ein sehr heftiger Hagelsturm mit tennisballgroßen Körnern.
<agent>: Das klingt nach einem Extremwetter-Ereignis. Haben Sie Fotos der Schäden gemacht?
<customer>: Ja, die Windschutzscheibe ist gesprungen und die Motorhaube hat mehrere Dellen.
<agent>: Hagelschäden sind über die Teilkasko gedeckt. Wo befindet sich Ihr Fahrzeug jetzt?
<customer>: In einer Garage in Thun. Der ADAC hat es dorthin gebracht.
<agent>: Gut. Ich organisiere einen Experten für die Schadensbegutachtung. Können Sie morgen dort sein?
<customer>: Ja, das passt. Wird eine neue Windschutzscheibe sofort ersetzt?
<agent>: Bei Sicherheitsrisiken organisieren wir Express-Reparatur. Die Windschutzscheibe hat Priorität.
<customer>: Was ist mit den Dellen? Das Auto ist erst zwei Jahre alt.
<agent>: Bei einem neuen Fahrzeug wird professionell ausgebeult oder das Blech ersetzt für perfekte Optik.
<customer>: Wie lange bin ich ohne Auto?
<agent>: Für Hagelschäden stellen wir kostenlos einen Ersatzwagen bis zur Reparatur.""",
        "topics": ["4", "10"],
        "summary": "Customer's car damaged by severe hailstorm on highway. Agent arranges expert assessment, prioritizes windshield safety repair, and provides replacement vehicle."
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Pittet. Je travaille maintenant à 50% et me demande si je peux ajuster mes assurances.
<agent>: Bonjour Madame Pittet, ici Nicole Fankhauser. Quelle réduction d'activité avez-vous faite?
<customer>: Je suis passée de 100% à 50% pour m'occuper de mes enfants. Mon salaire a diminué de moitié.
<agent>: Avec moins de revenus, nous pourrions ajuster votre assurance perte de gain en conséquence.
<customer>: Qu'est-ce que cela changerait concrètement?
<agent>: La prime diminuerait proportionnellement, mais les prestations aussi en cas d'arrêt de travail.
<customer>: Et pour l'assurance vie? J'ai moins de besoins financiers maintenant.
<agent>: Vous pourriez réduire le capital-décès ou suspendre temporairement les primes.
<customer>: Suspension temporaire? Comment ça marche?
<agent>: Vous pouvez mettre la police en réduction de primes pendant quelques années, puis reprendre plus tard.
<customer>: C'est intéressant car je compte reprendre à temps plein quand les enfants seront plus grands.
<agent>: Parfait, cette flexibilité est prévue pour ces situations de vie.
<customer>: Pouvez-vous calculer les économies totales?
<agent>: Avec l'ajustement de l'assurance perte de gain et la suspension temporaire de l'assurance vie, vous économiseriez environ 150 francs par mois.""",
        "topics": ["6", "12"],
        "summary": "Customer reduced work to 50% for childcare and wants to adjust insurance coverage. Agent explains proportional premium reductions and temporary policy suspension options.",
        "suggested_topics": ["2"]
    },
    {
        "transcript": """<customer>: Hello, this is Mr. Walsh. I need to add coverage for my home-based business.
<agent>: Hello Mr. Walsh, this is Petra Giger from Vaudoise. What type of business do you operate from home?
<customer>: I'm a freelance graphic designer with about 20,000 francs worth of computer equipment.
<agent>: Home-based businesses need additional coverage beyond standard homeowner's insurance.
<customer>: What's the difference between personal and business property coverage?
<agent>: Personal policies exclude business equipment. You need professional coverage for computers, software, and business liability.
<customer>: Do I need liability coverage if clients never visit my home?
<agent>: Yes, for professional errors, data loss, or if your work causes financial harm to clients.
<customer>: I sometimes work with confidential client data. Is cyber liability included?
<agent>: Cyber protection is essential for data breaches and should be added separately.
<customer>: What would be the total premium for equipment and liability coverage?
<agent>: For 20,000 francs equipment plus professional liability and cyber coverage, approximately 450 francs annually.
<customer>: That seems reasonable. Does it cover equipment anywhere or just at home?
<agent>: We can extend coverage for portable equipment when working at client locations.
<customer>: Perfect. I often work at coffee shops with my laptop. Let's include mobile coverage.""",
        "topics": ["3", "9"],
        "summary": "Freelance graphic designer needs home-based business insurance for equipment and professional liability. Agent explains business vs personal coverage and mobile equipment protection.",
        "suggested_topics": ["1"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Frau Steiner. Ich ziehe ins Ausland und muss meine Versicherungen klären.
<agent>: Guten Tag Frau Steiner, hier ist Ralph Ducret. In welches Land ziehen Sie und für wie lange?
<customer>: Nach Kanada für mindestens fünf Jahre. Mein Mann hat dort einen Job bekommen.
<agent>: Bei einer dauerhaften Auswanderung müssen die meisten Schweizer Versicherungen angepasst oder gekündigt werden.
<customer>: Auch die Lebensversicherung? Die läuft seit 15 Jahren.
<agent>: Lebensversicherungen können oft fortgeführt werden, aber mit speziellen Bedingungen für Auslandwohnsitz.
<customer>: Welche Bedingungen sind das?
<agent>: Prämien müssen weiterhin in Schweizer Franken bezahlt werden und Leistungen erfolgen nach Schweizer Recht.
<customer>: Das sollte kein Problem sein. Was ist mit der Hausrat- und Autoversicherung?
<agent>: Diese müssen gekündigt werden, da sie nur für Schweizer Wohnsitze gelten.
<customer>: Kann ich meine Schadenfreiheitsrabatte in Kanada nutzen?
<agent>: Ja, wir stellen Ihnen eine internationale Schadensfreiheitsbestätigung aus.
<customer>: Gibt es noch andere Dokumente die ich brauche?
<agent>: Ich erstelle Ihnen ein komplettes Auswanderungspaket mit allen Bestätigungen und Kündigungen.
<customer>: Das wäre sehr hilfreich. Wann sollte ich das alles regeln?
<agent>: Am besten 4-6 Wochen vor dem Umzug, damit alle Formalitäten rechtzeitig abgewickelt sind.""",
        "topics": ["1", "12"],
        "summary": "Customer emigrating to Canada needs to adjust insurance policies. Agent explains continuation options for life insurance and provides emigration documentation package.",
        "suggested_topics": ["5"]
    },
    {
        "transcript": """<customer>: Bonjour, c'est Madame Dufour. Mon mari vient de recevoir un diagnostic de maladie grave.
<agent>: Bonjour Madame Dufour, ici Catherine Bloch. Je suis désolée d'apprendre cela. Comment puis-je vous aider?
<customer>: Nous avons une assurance vie mais je ne sais pas si elle couvre ce type de situation.
<agent>: Quelle maladie a été diagnostiquée, si vous permettez cette question?
<customer>: Un cancer du poumon. Les médecins parlent de chimiothérapie intensive.
<agent>: Notre assurance vie standard inclut une couverture pour maladies graves. Laissez-moi vérifier votre police.
<customer>: Qu'est-ce que cela signifie concrètement?
<agent>: En cas de diagnostic de cancer, vous pouvez recevoir jusqu'à 50% du capital-décès de façon anticipée.
<customer>: Vraiment? Cela nous aiderait énormément avec les frais médicaux.
<agent>: Exactement. Ce versement anticipé est prévu pour les situations comme la vôtre.
<customer>: Quelles démarches faut-il entreprendre?
<agent>: Il nous faut un rapport médical détaillé confirmant le diagnostic et le stade de la maladie.
<customer>: Le médecin nous a donné tous les documents aujourd'hui.
<agent>: Parfait. Je vous envoie le formulaire de demande et nous traiterons votre dossier en priorité.""",
        "topics": ["12", "7"],
        "summary": "Wife inquires about life insurance coverage after husband's cancer diagnosis. Agent explains critical illness benefits allowing advance capital payment for medical expenses.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Guten Tag, hier ist Herr Bachmann. Ich brauche Hilfe bei einem Verkehrsunfall mit einem Ausländer.
<agent>: Guten Tag Herr Bachmann, hier ist Sarah Lüthi. Was ist passiert und wo war der Unfall?
<customer>: Auf der Autobahn bei Genf. Ein französischer LKW ist mir hinten draufgefahren.
<agent>: Sind Sie verletzt worden?
<customer>: Nein, aber mein Auto hat erhebliche Schäden am Heck. Der LKW-Fahrer hatte keine Schweizer Versicherung.
<agent>: Bei Ausländern läuft die Abwicklung über das Büro Schweizer Versicherer. Haben Sie einen Europäischen Unfallbericht ausgefüllt?
<customer>: Ja, aber der LKW-Fahrer sprach nur französisch und ich bin mir nicht sicher, ob alles korrekt ist.
<agent>: Das macht nichts. Wichtig ist, dass Sie Fotos gemacht und die Polizei gerufen haben?
<customer>: Beides ja. Die Polizei bestätigte die Schuld des LKW-Fahrers.
<agent>: Perfekt. Wir übernehmen alle Verhandlungen mit der französischen Versicherung.
<customer>: Wie lange dauert das normalerweise?
<agent>: Bei klaren Schuldverhältnissen etwa 4-6 Wochen. Bis dahin können Sie unseren Reparaturservice nutzen.
<customer>: Und was ist mit einem Mietauto?
<agent>: Das organisieren wir sofort. Sie bekommen einen gleichwertigen Ersatzwagen bis zur Reparatur.""",
        "topics": ["4", "10"],
        "summary": "Customer involved in highway accident with French truck driver. Agent handles international insurance coordination and provides immediate replacement vehicle service.",
        "suggested_topics": ["4"]
    },
    {
        "transcript": """<customer>: Hello, this is Ms. Williams. I need to report damage to my valuable jewelry.
<agent>: Hello Ms. Williams, this is François Dubois from Vaudoise. I'm sorry to hear about the damage. Can you tell me what happened?
<customer>: I was at a wedding and my pearl necklace broke. The pearls scattered everywhere and many are missing.
<agent>: That must have been distressing. Is this necklace listed on your valuables coverage?
<customer>: Yes, it was appraised at 12,000 francs two years ago when I added it to my policy.
<agent>: Good. For jewelry claims, we'll need the original appraisal and photos of the damage if possible.
<customer>: I took photos at the scene and still have about half the pearls. Is it repairable?
<agent>: We'll arrange for a jewelry specialist to assess whether restoration is possible or if replacement is necessary.
<customer>: If it can't be repaired, will you pay the full appraised value?
<agent>: The settlement will be based on current market value, which may differ from the original appraisal.
<customer>: Should I get a new appraisal for the current value?
<agent>: Our jewelry expert will provide a current valuation as part of the claims process.
<customer>: How long does this type of claim usually take?
<agent>: Jewelry claims typically take 2-3 weeks once we have all documentation and expert assessment.""",
        "topics": ["13", "4"],
        "summary": "Customer reports damage to expensive pearl necklace at wedding. Agent arranges specialist assessment for repair vs replacement and explains valuation process.",
        "suggested_topics": ["4"]
    }
]