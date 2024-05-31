verification_email_body = """
<html>

<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            background-color: #fff;
        }

        h2 {
            color: #333;
        }

        ul {
            list-style-type: disc;
            padding-left: 20px;
        }

        p {
            margin-bottom: 15px;
        }

        .note {
            font-style: italic;
            color: #888;
        }

        /* Center the logo */
        .logo-container {
            text-align: center;
        }

        /* Adjust logo width if needed */
        .logo-container img {
            max-width: 100%;
        }
    </style>
</head>

<body>
    <div class="container">
        <div class="logo-container">
            <img src="https://github.com/abdulrafay97/EfficientSkinDis/assets/80894764/40ca29cd-8bc5-4ef5-9556-6f090373f531"
                alt="CompetitionAI Logo">
        </div>
        <h2>Welcome to CompetitionAI!</h2>
        <p>Hello and welcome to CompetitionAI!</p>
        <p>Thank you very much for signing up. To ensure the security of your account, we have generated a verification
            code for you: <strong>XXXXXX</strong>. Please use this code to verify your email address using our website.</p>
        <p>If you did not initiate this registration or if you believe you received this message by mistake, kindly
            disregard it. Your privacy and data security are of utmost importance to us.</p>
        <p>Should you have any questions or feedback, don't hesitate to contact us at <a
                href="mailto:info@competitionlaw.ai">info@competitionlaw.ai</a></p>
        <p>Many thanks,<br>The CompetitionAI Team</p>
    </div>
</body>

</html>
"""

approval_email_body = """
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Welcome to CompetitionAI</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
            border: 1px solid #ccc;
            border-radius: 5px;
            background-color: #f9f9f9;
        }
        h1 {
            font-size: 24px;
            text-align: center;
        }
        h2 {
            font-size: 20px;
            margin-top: 20px;
        }
        p {
            font-size: 16px;
            margin: 10px 0;
        }
        ul {
            list-style-type: disc;
            margin-left: 20px;
        }
        a {
            color: #007BFF;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        /* Center the logo */
        .logo-container {
            text-align: center;
        }

        /* Adjust logo width if needed */
        .logo-container img {
            max-width: 100%;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo-container">
                <img src="https://github.com/abdulrafay97/EfficientSkinDis/assets/80894764/40ca29cd-8bc5-4ef5-9556-6f090373f531"
                    alt="CompetitionAI Logo">
        </div>
        <h1>Welcome to CompetitionAI!</h1>
        <p>Your access to CompetitionAI has now been approved. You may sign in to use your account using <a href="https://www.competitionlaw.ai">www.competitionlaw.ai</a>. Please see below an explanation of how to use CompetitionAI and how to get the best results.</p>
        
        <h2>How does it work?</h2>
        <ul>
            <li>Go to <a href="https://www.competitionlaw.ai">www.competitionlaw.ai</a> and sign in to your account</li>
            <li>Choose a competition law source – CompetitionAI will search thousands of pages of guidance contained in that collection of sources to identify the relevant information</li>
            <li>Type your question in the box</li>
            <li>Click on the sources below to see the source text used to generate the answer</li>
        </ul>

        <h2>How to get the best results?</h2>
        <p>CompetitionAI works by matching questions with the most relevant text from thousands of pages of guidance from competition authorities to generate answers. Here’s how you can get the best results:</p>
        <ul>
            <li>Use the similar language to the competition authority – this will make it easier to identify the relevant text</li>
            <li>Ask one question at a time – it is easier for the model to identify the relevant sources if it only needs to answer one question at a time</li>
            <li>Be specific – the more focused the question, the more focused the answer</li>
            <li>Understand the sources – the model can only provide answers to questions using information contained in the underlying sources, therefore you will get best results if answers that are sought are contained in the relevant guidance</li>
            <li>Never rely on results and always check original sources – CompetitionAI is a cutting-edge research tool, it is not legal advice, and there may be errors, therefore a qualified lawyer should always independently verify the answers using original source documents.</li>
            <li>Never input confidential information into the website – do not input confidential information</li>
            <li>Provide feedback – this is an advanced testing version and we’re constantly trying to improve the results and interface so please let us know if you have any ideas or feedback using <a href="mailto:info@competitionlaw.ai">info@competitionlaw.ai</a>. We’d love to hear from you!</li>
        </ul>

        <p>If you have any feedback or you’d like to get in touch, please contact <a href="mailto:info@competitionlaw.ai">info@competitionlaw.ai</a></p>

        <p>By using CompetitionAI, you agree to be bound by the <a href="https://www.competitionlaw.ai/terms-and-conditions">Terms of Use</a></p>

        <p>Many thanks,<br>The CompetitionAI Team</p>
    </div>
</body>
</html>
"""

user_login_email_body = ''''
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 600px;
            margin: 0 auto;
        }
        h1 {
            color: #333;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin-bottom: 10px;
        }
        p {
            color: #555;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>New User Signup Request</h1>

        <p>
            Dear Admin,
        </p>

        <p>
            I hope this message finds you well. Our system has generated a new user signup request with the following details:
        </p>

        <ul>
            <li><strong>Name:</strong> aaaaaa</li>
            <li><strong>Email:</strong> bbbbbb</li>
            <li><strong>Company:</strong> cccccc</li>
            <li><strong>Position:</strong> dddddd</li>
        </ul>

        <p>
            Best regards,
        </p>
    </div>
</body>
</html>
'''