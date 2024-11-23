// src/Hero.js
import React from "react";

function Hero() {
  return (
    <section
      className="relative flex h-screen items-center justify-center bg-cover bg-center text-white"
      style={{ backgroundImage: "url('/hero.jpg')" }}
    >
      <div className="absolute inset-0 bg-gray-900 opacity-70"></div>
      <div className="relative flex flex-col items-center text-center">
        <h1 className="text-5xl font-bold md:text-6xl">
          Online System for Detecting <br className="lg:block" /> Website
          Vulnerabilities
        </h1>
        <p className="mt-6 max-w-2xl text-lg text-gray-400 md:text-xl">
          Stay ahead of threats by scanning your website for vulnerabilities.
          Ensure your web presence is secure and reliable.
        </p>
        <div className="mt-10">
          <button
            className="rounded-lg bg-blue-600 px-8 py-4 text-lg font-semibold text-white transition duration-300 hover:bg-blue-700"
            onClick={() =>
              document
                .getElementById("scanner-section")
                .scrollIntoView({ behavior: "smooth" })
            }
          >
            Get Started
          </button>
        </div>
      </div>
    </section>
  );
}

export default Hero;
