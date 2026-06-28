import React from "react";
import RetroGrid from "./ui/retro-grid";
import AnimatedShinyText from "./ui/animated-shiny-text";
import { motion } from "framer-motion";

interface MagicHeroProps {
  title: string;
  subtitle: string;
}

const MagicHero: React.FC<MagicHeroProps> = ({ title, subtitle }) => {
  return (
    <div className="relative flex h-[350px] w-full flex-col items-center justify-center overflow-hidden rounded-lg border border-slate-200 bg-[#F8FAFC] shadow-sm mb-4">
      <div className="z-10 flex flex-col items-center justify-center min-h-[10rem]">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="mb-4"
        >
          <AnimatedShinyText className="inline-flex items-center justify-center px-4 py-1 transition ease-out hover:text-slate-800 hover:duration-300">
            <span className="text-4xl md:text-5xl font-extrabold tracking-tight text-[#0052A3]">
              {title}
            </span>
          </AnimatedShinyText>
        </motion.div>
        
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 1, delay: 0.4 }}
          className="text-lg md:text-xl text-slate-600 text-center max-w-[600px] font-medium"
        >
          {subtitle}
        </motion.p>
      </div>

      <RetroGrid />
    </div>
  );
};

export default MagicHero;
