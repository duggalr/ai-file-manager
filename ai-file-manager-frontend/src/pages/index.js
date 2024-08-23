import { useState, useEffect } from 'react';
import AOS from 'aos';
import 'aos/dist/aos.css';
import axios from 'axios';
import Link from 'next/link';


const Landing = () => {
  
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [subscriberCount, setSubscriberCount] = useState(127);
  
    const handleSubmit = async (event) => {
        event.preventDefault();
        setLoading(true);

        let data = JSON.stringify({ email });
        console.log('data:', data)

        const apiUrl = 'http://127.0.0.1:8000/api/handle_email_submission';
        let response = await axios.post(
            apiUrl,
            data
        );
        console.log('res', response);

        let response_data = response.data;
        if (response_data['success'] === true){
            let new_subscriber_count = 127 + response_data['total_email_subscribers'];
            setSubscriberCount(new_subscriber_count);
            setSuccessMessage(true);
        } else{
            if ('duplicate' in res){
                setSuccessMessage(true);
            } else{
                // error occured
                setErrorMessage('An unexpected error occurred. Please try again later.');
            }
        }

    };

    useEffect(() => {
        AOS.init({
        duration: 1000, // Animation duration (ms)
        easing: 'ease-in-out', // Easing function
        once: true, // Whether animation should happen only once
        });
    }, []);

    useEffect(() => {
        
        // Function to fetch subscriber count
        const fetchSubscriberCount = async () => {
            try {
                const response = await axios.post('http://127.0.0.1:8000/api/get_email_subscriber_count');
                setSubscriberCount(response.data.total_email_subscribers);
                setLoading(false);
            } catch (error) {
                // setError('Failed to fetch subscriber count');
                setLoading(false);
            }
        };

        // Call the function
        fetchSubscriberCount();

    }, []);  // Empty dependency array ensures this runs only once on mount

    return (

        <>

            {/* <div className="min-h-screen flex flex-col bg-gray-100 dark:bg-gray-900 text-black dark:text-white transition-colors duration-300"> */}

                {/* Header */}
                <header className="text-center py-12 mt-10 relative overflow-hidden" data-aos="fade-in">

                    <div className="absolute inset-x-0 top-4 flex justify-center z-10">
                        <span className="inline-block bg-gray-200 text-gray-800 dark:bg-gray-800 dark:text-gray-400 font-normal px-3 py-0.5 rounded-lg shadow-md border border-gray-300 dark:border-gray-700 text-[13px]">
                            &#10024; Launching Soon &#10024;
                        </span>
                    </div>
                    
                    <h1 
                        className="text-[48px] font-bold leading-tight text-5xl font-poppins bg-gradient-to-r from-blue-400 via-purple-500 to-blue-400 bg-clip-text text-transparent mt-3"
                    >
                        File Companion
                    </h1>
                
                    <p className="text-gray-600 dark:text-gray-400 mb-12 mt-4 tracking-normal text-[23px]">
                        An AI that will semantically organize your existing and new files, so you don&apos;t have to...
                    </p>
                
                    {/* <div id="email_form_div" className="flex justify-center items-center space-x-2">
                        <form id="emailForm">                        
                            <input 
                                type="email" 
                                name="email"
                                id="emailInput" 
                                placeholder="Enter your email" 
                                class="px-4 py-3 mr-2 rounded-full border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-96 text-black dark:text-gray-400 bg-gray-200 dark:bg-gray-800"
                                required
                            />
                            <button type="submit" id="submitBtn" className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-6 py-3 rounded-full hover:from-purple-600 hover:to-blue-600 transition">
                                Join Waitlist
                            </button>
                        </form>
                    </div> */}

                    <div id="email_form_div" className="flex justify-center items-center space-x-2">
                        {!successMessage ? (
                            <form onSubmit={handleSubmit} id="emailForm">
                                <input
                                    type="email"
                                    name="email"
                                    id="emailInput"
                                    placeholder="Enter your email"
                                    className="px-4 py-3 mr-2 rounded-full border border-gray-300 dark:border-gray-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent w-96 text-black dark:text-gray-400 bg-gray-200 dark:bg-gray-800"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                />
                                <button
                                    type="submit"
                                    id="submitBtn"
                                    className="bg-gradient-to-r from-purple-500 to-blue-500 text-white px-6 py-3 rounded-full hover:from-purple-600 hover:to-blue-600 transition"
                                    disabled={loading}
                                >
                                    {loading ? 'Joining...' : 'Join Waitlist'}
                                </button>
                            </form>
                        ) : (
                            <div id="successMessage" className="mt-0 text-center">
                                <p className="text-[15px] bg-green-800 text-gray-300 py-2 px-4 rounded-full inline-block">
                                    Thanks for joining the waitlist! 🙏 You&apos;ll be the first to know when we launch!
                                </p>
                            </div>
                        )}
                    </div>

                    {errorMessage && (
                    <div className="mt-4 text-red-600">
                        <p>{errorMessage}</p>
                    </div>
                    )}
                                    
                    <div id="successMessage" className="hidden mt-4 text-center">
                        <p className="text-[15px] bg-green-800 text-gray-300 py-2 px-4 rounded-full inline-block">Thanks for joining the waitlist! 🙏 You&apos;ll be the first to know when we launch!</p>
                    </div>
                
                    <p className="text-gray-600 dark:text-gray-400 mt-3 text-[14px]">
                        <strong id="subscriber_count">{ subscriberCount }</strong> people are (not so patiently) waiting. &#128517;
                    </p>

                    <div className="relative text-center mt-0">
                        <svg width="100%" height="500px" viewBox="0 0 1000 500">
                            <foreignObject x="13" y="68" width="30" height="30">
                                <i className="fa-solid fa-file-excel text-blue-500"></i>
                            </foreignObject>
                            <path d="M 50,80 C 300,80 200,250 500,250" stroke="#3b82f6" stroke-width="4" fill="transparent" />
                            <circle cx="50" cy="80" r="10" fill="#3b82f6" />
                    
                            <foreignObject x="13" y="148" width="30" height="30">
                                <i className="fa-solid fa-file-pdf text-purple-500"></i>
                            </foreignObject>
                            <path d="M 50,160 C 300,160 200,250 500,250" stroke="#8b5cf6" stroke-width="4" fill="transparent" />
                            <circle cx="50" cy="160" r="10" fill="#8b5cf6" />
                    
                            <foreignObject x="13" y="228" width="30" height="30">
                                <i className="fa-solid fa-file-code text-yellow-400"></i>
                            </foreignObject>
                            <path d="M 50,240 C 300,240 200,250 500,250" stroke="#fde047" stroke-width="4" fill="transparent" />
                            <circle cx="50" cy="240" r="10" fill="#fde047" />
                    
                            <foreignObject x="13" y="308" width="30" height="30">
                                <i className="fa-solid fa-file-word text-orange-500"></i>
                            </foreignObject>
                            <path d="M 50,320 C 300,320 200,250 500,250" stroke="#f97316" stroke-width="4" fill="transparent" />
                            <circle cx="50" cy="320" r="10" fill="#f97316" />
                    
                            <foreignObject x="13" y="388" width="30" height="30">
                                <i className="fa-solid fa-photo-film text-green-500"></i>
                            </foreignObject>
                            <path d="M 50,400 C 300,400 200,250 500,250" stroke="#22c55e" stroke-width="4" fill="transparent" />
                            <circle cx="50" cy="400" r="10" fill="#22c55e" />
                    
                            <path d="M 500,250 C 800,250 700,150 950,150" stroke="#3b82f6" stroke-width="4" fill="transparent" />
                            <path d="M 500,250 C 800,250 700,150 950,150" stroke="#8b5cf6" stroke-width="4" fill="transparent" />
                    
                            <path d="M 500,250 C 800,250 700,250 950,250" stroke="#fde047" stroke-width="4" fill="transparent" />
                            <path d="M 500,250 C 800,250 700,250 950,250" stroke="#f97316" stroke-width="4" fill="transparent" />
                    
                            <path d="M 500,250 C 800,250 700,350 950,350" stroke="#22c55e" stroke-width="4" fill="transparent" />
                    
                            <foreignObject x="950" y="138" width="30" height="30">
                                <i className="fas fa-folder text-blue-500"></i>
                            </foreignObject>
                            <foreignObject x="950" y="238" width="30" height="30">
                                <i className="fas fa-folder text-purple-500"></i>
                            </foreignObject>
                            <foreignObject x="950" y="338" width="30" height="30">
                                <i className="fas fa-folder text-yellow-400"></i>
                            </foreignObject>
                    
                            <rect x="420" y="225" width="160" height="44" fill="#8E39EA" rx="8" ry="8"/>
                            <text x="501" y="249" fill="#ffffff" font-size="19px" font-family="Arial" text-anchor="middle" dominant-baseline="middle">
                                File Companion
                            </text>

                        </svg>
                    </div>

                </header>

                {/* Blog Section */}
                <section id="blog" className="py-0 dark:bg-gray-900 mt-3" data-aos="fade-in">
                    <div className="max-w-4xl mx-auto px-4">
                        <h2 className="text-[40px] font-bold text-center mb-4 bg-gradient-to-r from-blue-500 via-purple-600 to-blue-700 bg-clip-text text-transparent">
                            Blog
                        </h2>
                        <p className="text-gray-600 dark:text-gray-400 text-center tracking-wide text-[17px]">
                            Join us on our journey as we build in public, and share the unique challenges we&apos;ve tackled along the way.
                        </p>
                        
                        <div className="flex justify-center mt-12">
                            <Link href="/blog/welcome">
                                <div className="max-w-2xl p-6 bg-gray-100 border border-gray-200 rounded-lg shadow dark:bg-gray-800 dark:border-gray-700 transform transition-transform duration-300 ease-in-out hover:translate-y-1 cursor-pointer">
                                    <h5 className="mb-2 text-2xl font-bold tracking-tight text-gray-700 dark:text-gray-300">
                                        Blog Post #1: Welcome
                                    </h5>
                                    <p className="mb-3 font-normal text-gray-500 dark:text-gray-400 mt-5">
                                        We are taking the mindset of “building and growing in public,” with the hope of fostering a like-minded community along the way.
                                        The purpose of this blog is to document the development journey of File Companion from the beginning... 
                                    </p>                                    
                                </div>
                            </Link>
                        </div>
                    </div>
                </section>

            {/* </div> */}
        
        </>

    );

}

export default Landing;