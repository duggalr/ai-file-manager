import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';

const LandingNavBar = () => {
    const [theme, setTheme] = useState('dark');

    useEffect(() => {
        const savedTheme = localStorage.getItem('color-theme') || 'dark';
        setTheme(savedTheme);
        document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    }, []);

    const toggleTheme = () => {
        const newTheme = theme === 'dark' ? 'light' : 'dark';
        setTheme(newTheme);
        document.documentElement.classList.toggle('dark', newTheme === 'dark');
        localStorage.setItem('color-theme', newTheme);
    };

    const router = useRouter();
    const { pathname } = router;

    return (
        <nav className="flex justify-between items-center p-6 px-14">
            <div className="text-3xl font-bold cursor-pointer hover:text-blue-400">
                <a href="/">
                    <i className="fa-brands fa-nfc-directional"></i>
                </a>
            </div>
            <div className="justify-center space-x-8">
                {/* <a href="#blog" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Blog</a>
                <a href="#contact" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Contact</a> */}

                {pathname === '/' && (
                    <>
                        <a href="#blog" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Blog</a>
                        <a href="#contact" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Contact</a>
                    </>
                )}

                {pathname === '/blog/welcome' && (
                    <>
                        <a href="/" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Home</a>
                        <a href="#contact" className="text-gray-400 hover:text-blue-400 transition text-[16.5px]">Contact</a>
                    </>
                )}


            </div>
            <div>
                {/* <button
                    onClick={toggleTheme}
                    className="bg-gray-300 text-black dark:bg-gray-600 dark:text-white p-2 rounded-full"
                >
                    {theme === 'dark' ? 'Light Mode' : 'Dark Mode'}
                </button> */}

                {/* <button
                    id="theme-toggle"
                    type="button"
                    className="text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-gray-200 dark:focus:ring-gray-700 rounded-lg text-sm p-2.5"
                >

                    {
                        theme === 'dark' 
                        ? 
                        <svg
                            id="theme-toggle-light-icon"
                            className="w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
                            ></path>
                        </svg>
                        : 
                        <svg
                            id="theme-toggle-dark-icon"
                            className="hidden w-5 h-5"
                            fill="currentColor"
                            viewBox="0 0 20 20"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                                fill-rule="evenodd"
                                clip-rule="evenodd"
                            ></path>
                        </svg>
                    }
                    
                </button> */}

<div onClick={toggleTheme} className="cursor-pointer">
    {theme === 'dark' ? (
        <svg
            id="theme-toggle-light-icon"
            className="w-5 h-5"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z"
            ></path>
        </svg>
    ) : (
        <svg
            id="theme-toggle-dark-icon"
            className="w-5 h-5"
            fill="currentColor"
            viewBox="0 0 20 20"
            xmlns="http://www.w3.org/2000/svg"
        >
            <path
                d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z"
                fillRule="evenodd"
                clipRule="evenodd"
            ></path>
        </svg>
    )}
</div>


            </div>
        </nav>
    );
};

export default LandingNavBar;