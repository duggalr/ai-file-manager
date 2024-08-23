import { Html, Head, Main, NextScript } from 'next/document';
 
export default function Document() {
    return (
        <Html>
            <Head>
                <title>File Companion</title>
                <link rel="shortcut icon" href="/favicon.ico" />
                <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==" crossorigin="anonymous" referrerpolicy="no-referrer" />
            </Head>
            <body>
                <Main />
                <NextScript />
            </body>
        </Html>
    )
};