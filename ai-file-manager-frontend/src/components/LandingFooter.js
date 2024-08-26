import Link from 'next/link';

const LandingFooter = () => {

    return (

        <footer className="bg-gray-200 dark:bg-gray-800 p-4 mt-40">
            <div className="flex justify-between max-w-full mx-auto">
                <div className="font-bold text-violet-500 dark:text-violet-500 text-[23px]">
                    File Companion
                    <span className="pl-3 space-x-3">
                        <Link href="https://x.com/filecompanion" className="text-gray-400 dark:text-gray-400 text-base hover:text-blue-400 dark:hover:text-blue-400">
                            <i className="fa-brands fa-twitter"></i>
                        </Link>
                    </span>
                </div>

                <div className="text-gray-600 dark:text-gray-400 space-x-4 pt-2">
                    {/* <a href="mailto:duggalr42@gmail.com" className="hover:text-blue-400">Contact Us</a> */}
                    <span className="hover:text-blue-400">
                        rahul@filecompanion.app
                    </span>
                </div>
            </div>
        </footer>

    );

};

export default LandingFooter;