import { useEffect, useState } from 'react';

const LandingFooter = () => {

    return (

        <footer class="bg-gray-200 dark:bg-gray-800 p-4 mt-40">
            <div class="flex justify-between max-w-full mx-auto">
                <div class="font-bold text-violet-500 dark:text-violet-500 text-[23px]">
                    File Companion
                    <span class="pl-3 space-x-3">
                        <a href="https://github.com/" class="text-gray-400 dark:text-gray-400 text-base hover:text-blue-400 dark:hover:text-blue-400">
                            <i class="fa-brands fa-twitter"></i>
                        </a>
                        <a href="https://github.com/" class="text-gray-400 dark:text-gray-400 text-base hover:text-blue-400 dark:hover:text-blue-400">
                            <i class="fa-brands fa-linkedin"></i>
                        </a>
                    </span>
                </div>

                <div class="text-gray-600 dark:text-gray-400 space-x-4 pt-2">
                    <a href="#" target="_blank" rel="noopener noreferrer" class="hover:text-blue-400">Contact Us</a>
                </div>
            </div>
        </footer>

    );

};

export default LandingFooter;