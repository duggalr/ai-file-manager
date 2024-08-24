import { useEffect } from 'react';
import Link from 'next/link';
import AOS from 'aos';
import 'aos/dist/aos.css';


const WelcomeBlog = () => {

    useEffect(() => {
        AOS.init({
        duration: 500, // Animation duration (ms)
        easing: 'ease-in-out', // Easing function
        once: true, // Whether animation should happen only once
        });
    }, []);
    
    return (

        <>

            <div class="flex justify-center py-3">
                
                <div class="max-w-4xl p-8 rounded-lg bg-gray-100 dark:bg-gray-900">
                    
                    <h1 class="text-4xl font-bold mb-4 text-center tracking-normal text-violet-500">
                        Welcome to File Companion
                    </h1>

                    <div class="flex justify-center items-center text-center">
                        <img
                        class="w-8 h-8 rounded-full mr-2"
                        src="https://yt3.googleusercontent.com/E97CuvpnWOwM0pmsC4P-ghXTKwWNNFTTusFPWs5yydxaDHLoD6bHWgwixI6ipAe7IyBiWUgg2A=s160-c-k-c0x00ffffff-no-rj"
                        alt="Rahul Duggal" />
                        <span class="text-gray-700 dark:text-gray-400">Rahul Duggal</span>
                        <span class="mx-4 text-gray-400">|</span>
                        <div class="text-gray-700 dark:text-gray-400">
                            <span class="font-semibold">
                                <i class="fa-solid fa-calendar-days"></i>
                            </span>&nbsp;August 22, 2024
                        </div>
                    </div>
                    
                    <hr class="h-px my-8 bg-gray-200 border-0 dark:bg-gray-700" />

                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                        Welcome! &#128075;
                        The purpose of this blog is to document the development journey of File Companion from the beginning. 
                        As we build this project, we aim to share our insights, highlight both the technical and non-technical challenges we encounter, 
                        and provide a glimpse into the problems we&apos;re tackling next.
                    </p>

                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                        We are taking the mindset of “building and growing in public,” with the hope of fostering a like-minded community along the way.
                    </p>

                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                        For this first post, we&apos;ll provide some context about the problem we&apos;re addressing and why we decided to work on File Companion.
                    </p>
                    
                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-10">
                        The Problem
                    </h2>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed">
                        We live in an age of information overload. With an immense amount of data at our fingertips, keeping it organized, up-to-date, 
                        and easily retrievable has become increasingly challenging. While Google and various AI startups are doing great work organizing 
                        information on the web, there remains a significant gap in tools that help individuals manage their personal information—whether that&apos;s 
                        files, cloud drives, bookmarks, or physical notes. Our goal with File Companion is to address this gap, beginning with a focus on personal file management.
                    </p>

                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-10" data-aos="fade-in">
                        Proposed Solution
                    </h2>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        The goal of File Companion is to work seamlessly in the background as a desktop application, 
                        automatically organizing your files in a way that you find semantically meaningful.
                        We want the app to be as flexible as possible, in how the your files are organized and presented to you.
                        Initially, the app will present your files in the form of entities, categories, and sub-categories.
                        We will describe the technical details in a future blog post.
                    </p>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        For our first version, which we&apos;re currently hard at work on, the AI will analyze the content of each file and categorize it based on the semantic entities it detects.
                        The result is an organized system that makes your data easy to view and manage. 
                    </p>

                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        Additionally, the application will feature a powerful semantic search function, accessible 
                        via a keyboard shortcut, allowing you to quickly find and open the information you need, whenever you need it.
                    </p>

                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-10" data-aos="fade-in">Security and Privacy</h2>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        From the beginning, we&apos;ve placed a strong emphasis on security and data privacy. <strong>Your file data will never be stored on our servers or in our database.</strong> Instead, it&apos;s processed 
                        in memory and transmitted to our hosted LLM in an encrypted format, where it&apos;s immediately deleted after processing. We only store very preliminary metadata about your files, 
                        along with the categorization data generated by the LLM.
                    </p>

                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        Privacy and Security is critical to us, and we will adhere to the strongest security principles as we continue to build out the application.
                    </p>

                    <h2 class="text-2xl font-semibold text-gray-900 dark:text-white mb-4 mt-10" data-aos="fade-in">What&apos;s Next</h2>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        In the coming blog posts, we&apos;ll dive deeper into the technical details of the project and highlight the challenges we&apos;ve faced—and those we anticipate—as we continue building out the application.
                    </p>
                    <p class="text-lg text-gray-700 dark:text-gray-300 mb-6 leading-relaxed" data-aos="fade-in">
                        In the meantime, if you&apos;re interested in this problem, have questions, or want to contribute, feel free to <Link href="mailto:rahul@filecompanion.app">reach out</Link>—we&apos;d love to hear from you!
                    </p>
                    <p class="text-lg text-gray-700 dark:text-gray-300 leading-relaxed" data-aos="fade-in">
                        The V1 will be out very soon, and we hope you are as excited as we are! 😅
                    </p>
                </div>

            </div>
                    
        </>

    );

}

export default WelcomeBlog;