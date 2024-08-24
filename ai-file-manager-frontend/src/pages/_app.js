import '@/styles/globals.css';
import LandingNavBar from '@/components/LandingNavBar';
import LandingFooter from '@/components/LandingFooter';

function MyApp({Component, pageProps}) {

    return (
        <>
            <div className="min-h-screen flex flex-col bg-gray-100 dark:bg-gray-900 text-black dark:text-white transition-colors duration-300">
                <LandingNavBar />
                <Component {...pageProps} />
                <LandingFooter />
            </div>
        </>
    );

}

export default MyApp;