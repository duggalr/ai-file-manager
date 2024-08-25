import { Html, Head, Main, NextScript } from 'next/document';
import { useState, useEffect } from 'react';
import Script from 'next/script';

 
export default function Document() {

    const heapEnvId = process.env.NEXT_PUBLIC_HEAP_ENV_ID;
    
    useEffect(() => {

        // Function to generate a unique user ID for anonymous users
        const generateUniqueUserId = () => {
            return `anon_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
        };

        // Function to set user identity
        const setUserIdentity = (userId) => {
            if (window.heap) {
                window.heap.identify(userId);
            }
        };

        // Generate and set user identity
        const userId = generateUniqueUserId();
        setUserIdentity(userId);

    }, []);

    return (
        <Html>
            <Head>
                <title>File Companion</title>
                <link rel="shortcut icon" href="/favicon.png" />
                <link rel="stylesheet" href="https://rsms.me/inter/inter.css" />
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.2/css/all.min.css" integrity="sha512-SnH5WK+bZxgPHs44uWIX+LLJAJ9/2PkPKZ5QiAj6Ta86w+fsb2TkcmfRyVX3pBnMFcV7oQPJkl9QevSCWr3W6A==" crossorigin="anonymous" referrerpolicy="no-referrer" />

                {/* Heap Analytics Script */}
                <script
                dangerouslySetInnerHTML={{
                    __html: `
                    window.heapReadyCb=window.heapReadyCb||[],window.heap=window.heap||[],heap.load=function(e,t){window.heap.envId=e,window.heap.clientConfig=t=t||{},window.heap.clientConfig.shouldFetchServerConfig=!1;var a=document.createElement("script");a.type="text/javascript",a.async=!0,a.src="https://cdn.us.heap-api.com/config/"+e+"/heap_config.js";var r=document.getElementsByTagName("script")[0];r.parentNode.insertBefore(a,r);var n=["init","startTracking","stopTracking","track","resetIdentity","identify","getSessionId","getUserId","getIdentity","addUserProperties","addEventProperties","removeEventProperty","clearEventProperties","addAccountProperties","addAdapter","addTransformer","addTransformerFn","onReady","addPageviewProperties","removePageviewProperty","clearPageviewProperties","trackPageview"],i=function(e){return function(){var t=Array.prototype.slice.call(arguments,0);window.heapReadyCb.push({name:e,fn:function(){heap[e]&&heap[e].apply(heap,t)}})}};for(var p=0;p<n.length;p++)heap[n[p]]=i(n[p])};
                    heap.load("${heapEnvId}");
                    `,
                }}
                />

                {/* Google Analytics Script */}
                <Script
                    async
                    src={`https://www.googletagmanager.com/gtag/js?id=G-ZHQCXN1986`}
                />
                <Script id="google-analytics" strategy="afterInteractive">
                    {`
                    window.dataLayer = window.dataLayer || [];
                    function gtag(){dataLayer.push(arguments);}
                    gtag('js', new Date());

                    gtag('config', 'G-ZHQCXN1986');
                    `}
                </Script>
                    
            </Head>
            <body>
                <Main />
                <NextScript />
            </body>
        </Html>
    )
};