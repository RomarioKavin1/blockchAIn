"use client";

import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import LogoComponent from "@/components/logo";
import CyberButton from "@/components/cyberButton";

const LandingPage = () => {
  const [windowSize, setWindowSize] = useState({ width: 1200, height: 800 });
  const [isMounted, setIsMounted] = useState(false);

  useEffect(() => {
    setWindowSize({
      width: window.innerWidth,
      height: window.innerHeight,
    });
    setIsMounted(true);

    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener("resize", handleResize);
    return () => window.removeEventListener("resize", handleResize);
  }, []);

  if (!isMounted) return null; // Prevent rendering until we have window size

  return (
    <div className="relative min-h-screen bg-black overflow-hidden">
      {/* Enhanced radial gradient background */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,#2563eb15_0%,transparent_50%)] animate-pulse" />
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_bottom,#7c3aed15_0%,transparent_50%)] animate-pulse delay-75" />

      {/* Enhanced cyber grid with multiple layers */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.3 }}
        transition={{ duration: 2 }}
        className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f15_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f15_1px,transparent_1px)] bg-[size:64px_64px]"
      />
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.2 }}
        transition={{ duration: 2 }}
        className="absolute inset-0 bg-[linear-gradient(to_right,#4f4f4f10_1px,transparent_1px),linear-gradient(to_bottom,#4f4f4f10_1px,transparent_1px)] bg-[size:32px_32px]"
      />

      {/* Animated particle system */}
      <div className="absolute inset-0">
        {[...Array(40)].map((_, i) => (
          <motion.div
            key={i}
            className={`absolute w-1 h-1 ${
              i % 2 === 0 ? "bg-purple-400/40" : "bg-cyan-400/40"
            } rounded-full`}
            initial={{
              x: Math.random() * windowSize.width,
              y: Math.random() * windowSize.height,
            }}
            animate={{
              y: [null, -windowSize.height],
              opacity: [0.8, 0],
            }}
            transition={{
              duration: Math.random() * 5 + 3,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>

      {/* Enhanced floating lines */}
      {[...Array(10)].map((_, i) => (
        <motion.div
          key={`line-${i}`}
          className="absolute h-40 w-px bg-gradient-to-b from-transparent via-purple-500/50 to-transparent"
          initial={{
            x: Math.random() * windowSize.width,
            y: -100,
            opacity: 0,
          }}
          animate={{
            y: [windowSize.height + 100],
            opacity: [0, 1, 0],
          }}
          transition={{
            duration: Math.random() * 3 + 4,
            repeat: Infinity,
            delay: Math.random() * 2,
          }}
        />
      ))}

      {/* Animated gradient orbs */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.5, 0.3],
          rotate: [0, 360],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear",
        }}
        className="absolute top-1/4 -left-32 w-96 h-96 bg-gradient-to-r from-purple-500/30 to-cyan-500/30 rounded-full blur-3xl"
      />
      <motion.div
        animate={{
          scale: [1.2, 1, 1.2],
          opacity: [0.3, 0.5, 0.3],
          rotate: [360, 0],
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          ease: "linear",
          delay: 4,
        }}
        className="absolute bottom-1/4 -right-32 w-96 h-96 bg-gradient-to-r from-cyan-500/30 to-purple-500/30 rounded-full blur-3xl"
      />

      {/* Scanlines effect */}
      <div className="absolute inset-0 pointer-events-none bg-[repeating-linear-gradient(0deg,#00000015,#00000015_1px,transparent_1px,transparent_2px)]" />

      {/* Main content */}
      <div className="relative z-10 min-h-screen flex flex-col items-center justify-center p-4 space-y-16">
        {/* Logo section with cyber frame */}
        <motion.div
          initial={{ y: -50 }}
          animate={{ y: 0 }}
          className="relative p-8 rounded-lg"
        >
          {/* Enhanced cyber frame */}
          <div className="absolute inset-0 bg-gradient-to-r from-purple-500/10 via-cyan-400/10 to-purple-500/10 rounded-lg opacity-35" />
          <div className="absolute inset-0 backdrop-blur-sm rounded-lg border border-purple-500/20" />

          {/* Corner decorations with animations */}
          {[
            "-top-1 -left-1",
            "-top-1 -right-1",
            "-bottom-1 -left-1",
            "-bottom-1 -right-1",
          ].map((position, i) => (
            <motion.div
              key={i}
              className={`absolute w-4 h-4 ${position}`}
              animate={{
                opacity: [1, 0.5, 1],
                scale: [1, 1.1, 1],
              }}
              transition={{
                duration: 2,
                repeat: Infinity,
                delay: i * 0.5,
              }}
            >
              <div className="absolute inset-0 border-2 border-cyan-400/50" />
              <div className="absolute inset-0 border-2 border-purple-500/50 transform translate-x-[1px] translate-y-[1px]" />
            </motion.div>
          ))}

          <div className="relative">
            <LogoComponent size="large" />
          </div>
        </motion.div>

        {/* Motto with enhanced effects */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8, duration: 0.8 }}
          className="text-xl md:text-2xl font-pixel text-center max-w-3xl relative p-4"
        >
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm rounded-lg -z-10" />
          <span
            className="relative inline-block text-transparent bg-clip-text bg-gradient-to-r 
            from-purple-400 via-cyan-400 to-purple-400
            drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]
            after:content-[''] after:absolute after:bottom-0 after:left-0 after:w-full after:h-[2px]
            "
          >
            Unleash the Power of AI Swarms in the Blockchain
          </span>
        </motion.div>

        {/* Enhanced launch button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2, duration: 0.8 }}
        >
          <CyberButton
            cyberSize="xl"
            glowColor="gradient"
            className="font-pixel"
            onClick={() => (window.location.href = "/dashboard")}
            hoverEffect="both"
          >
            Launch dApp
          </CyberButton>
        </motion.div>
      </div>
    </div>
  );
};

export default LandingPage;
