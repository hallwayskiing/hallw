import {
  Bird,
  Book,
  Brain,
  Cat,
  Coffee,
  Dumbbell,
  FileText,
  Film,
  Gamepad2,
  Ghost,
  Gift,
  Globe,
  Heart,
  Leaf,
  Lightbulb,
  Mail,
  MapPin,
  Moon,
  Music,
  Palette,
  Rocket,
  Search,
  ShoppingBag,
  Sparkles,
  Star,
  Sun,
  Utensils,
  Wand2,
  Zap,
} from "lucide-react";

import type { ColorName } from "./types";

export const ALL_QUICK_STARTS = [
  {
    icon: <Brain className="w-4 h-4" />,
    color: "cyan",
    text: "If animals could talk, which would be the most annoying at a dinner party?",
  },
  {
    icon: <Coffee className="w-4 h-4" />,
    color: "orange",
    text: "Design a cocktail inspired by finding a $20 bill in an old coat pocket.",
  },
  {
    icon: <Search className="w-4 h-4" />,
    color: "amber",
    text: "What are the most bizarre unsolved mysteries involving time travel?",
  },
  {
    icon: <Gamepad2 className="w-4 h-4" />,
    color: "purple",
    text: "Teach me a secret 'handshake' or coded language that only we know.",
  },
  {
    icon: <Film className="w-4 h-4" />,
    color: "blue",
    text: "What would my daily routine look like in a 90s cyberpunk anime?",
  },
  {
    icon: <Dumbbell className="w-4 h-4" />,
    color: "orange",
    text: "Design a workout routine for surviving a sudden zombie apocalypse.",
  },
  {
    icon: <Sparkles className="w-4 h-4" />,
    color: "pink",
    text: "What are real-life 'glitches in the matrix' that science can't explain?",
  },
  {
    icon: <Mail className="w-4 h-4" />,
    color: "emerald",
    text: "Write a polite breakup letter to my favorite spicy chips (heartburn).",
  },
  {
    icon: <Ghost className="w-4 h-4" />,
    color: "rose",
    text: "Help me name my future pet ghost (it's friendly but hides socks).",
  },
  {
    icon: <Rocket className="w-4 h-4" />,
    color: "blue",
    text: "If Earth was a video game, what would the latest patch notes say?",
  },
  {
    icon: <Utensils className="w-4 h-4" />,
    color: "yellow",
    text: "I need a recipe for a cake that looks like a brick but tastes like heaven.",
  },
  {
    icon: <Globe className="w-4 h-4" />,
    color: "cyan",
    text: "What are words in other languages that don't have direct translations?",
  },
  {
    icon: <Wand2 className="w-4 h-4" />,
    color: "purple",
    text: "Create a 'vibe check' quiz to determine what mythical creature I am.",
  },
  {
    icon: <Moon className="w-4 h-4" />,
    color: "blue",
    text: "Suggest a vacation spot for a dapper vampire who forgot sunscreen.",
  },
  {
    icon: <Leaf className="w-4 h-4" />,
    color: "emerald",
    text: "If my houseplants could text me, what would be their main complaint?",
  },
  {
    icon: <Book className="w-4 h-4" />,
    color: "teal",
    text: "Translate a movie quote into medieval English from a confused peasant.",
  },
  {
    icon: <Heart className="w-4 h-4" />,
    color: "rose",
    text: "What would be the most impractical superpower on a first date?",
  },
  {
    icon: <FileText className="w-4 h-4" />,
    color: "cyan",
    text: "Draft a legal contract with my cat regarding mandatory 3 AM zoomies.",
  },
  {
    icon: <Search className="w-4 h-4" />,
    color: "amber",
    text: "What's the weirdest thing ever found in a time capsule from the 1920s?",
  },
  {
    icon: <MapPin className="w-4 h-4" />,
    color: "emerald",
    text: "Where is the most creative place on Earth to hide a treasure chest?",
  },
  {
    icon: <Music className="w-4 h-4" />,
    color: "purple",
    text: "Compose a short lullaby for an AI having a minor existential crisis.",
  },
  {
    icon: <ShoppingBag className="w-4 h-4" />,
    color: "pink",
    text: "What clothing would we wear on a planet with 3x stronger gravity?",
  },
  {
    icon: <Brain className="w-4 h-4" />,
    color: "cyan",
    text: "List things that sound like insults but are actually compliments.",
  },
  {
    icon: <Lightbulb className="w-4 h-4" />,
    color: "yellow",
    text: "Plan a party where everyone dresses as a failed invention.",
  },
  {
    icon: <Book className="w-4 h-4" />,
    color: "teal",
    text: "What are 'forbidden' historical facts that sound too weird to be true?",
  },
  {
    icon: <Globe className="w-4 h-4" />,
    color: "blue",
    text: "What YouTube video represents humanity best for visiting aliens?",
  },
  {
    icon: <Palette className="w-4 h-4" />,
    color: "pink",
    text: "Describe the taste of 'electric blue' to someone who has never seen it.",
  },
  {
    icon: <Zap className="w-4 h-4" />,
    color: "yellow",
    text: "Write a haiku about a printer running out of magenta ink.",
  },
  {
    icon: <Bird className="w-4 h-4" />,
    color: "cyan",
    text: "What would a social media platform for squirrels look like?",
  },
  {
    icon: <Utensils className="w-4 h-4" />,
    color: "orange",
    text: "Create a workout using only items found in a kitchen pantry.",
  },
  {
    icon: <Star className="w-4 h-4" />,
    color: "amber",
    text: "What would be my gimmick as a low-budget superhero movie villain?",
  },
  {
    icon: <Gamepad2 className="w-4 h-4" />,
    color: "purple",
    text: "Which early 2000s web 'abandonware' desperately needs a comeback?",
  },
  {
    icon: <Brain className="w-4 h-4" />,
    color: "cyan",
    text: "A survival guide for talking to a hardcore conspiracy theorist.",
  },
  {
    icon: <Gift className="w-4 h-4" />,
    color: "rose",
    text: "Value of a cursed Victorian doll on Antiques Roadshow in 2088?",
  },
  {
    icon: <Globe className="w-4 h-4" />,
    color: "blue",
    text: "Write a short 'FAQ for Humans' by a confused alien tour guide.",
  },
  {
    icon: <Lightbulb className="w-4 h-4" />,
    color: "yellow",
    text: "Suggest 5 absurd ways to use a pool noodle (no water allowed).",
  },
  {
    icon: <Utensils className="w-4 h-4" />,
    color: "orange",
    text: "If I could only eat one texture for life, which is most versatile?",
  },
  {
    icon: <Coffee className="w-4 h-4" />,
    color: "amber",
    text: "Best 'fake names' for coffee orders to mildly confuse the barista?",
  },
  {
    icon: <Book className="w-4 h-4" />,
    color: "teal",
    text: "Start a story: 'You wake up in a room made of marshmallows'.",
  },
  {
    icon: <Search className="w-4 h-4" />,
    color: "blue",
    text: "Poorly planned historical 'heists' that actually somehow worked?",
  },
  {
    icon: <Brain className="w-4 h-4" />,
    color: "purple",
    text: "What 'captchas' would robots use to catch hiding humans?",
  },
  {
    icon: <Sun className="w-4 h-4" />,
    color: "orange",
    text: "Design a new zodiac sign for digital traits, like 'The Doomscroller'.",
  },
  {
    icon: <Dumbbell className="w-4 h-4" />,
    color: "emerald",
    text: "What's the most unusual forgotten sport in Olympic history?",
  },
  {
    icon: <Mail className="w-4 h-4" />,
    color: "cyan",
    text: "Write a 'Letter of Recommendation' for a toaster that never burns.",
  },
  {
    icon: <Music className="w-4 h-4" />,
    color: "pink",
    text: "Title of my dramatic solo musical song while waiting for the bus?",
  },
  {
    icon: <Cat className="w-4 h-4" />,
    color: "rose",
    text: "Creative ways to use 'I forgot' as a legitimate excuse for anything?",
  },
  {
    icon: <Film className="w-4 h-4" />,
    color: "amber",
    text: "Suggest a movie marathon for feeling like you're safely tripping.",
  },
  {
    icon: <Globe className="w-4 h-4" />,
    color: "blue",
    text: "What are the 'Seven Wonders' of the digital world today?",
  },
  {
    icon: <Moon className="w-4 h-4" />,
    color: "purple",
    text: "Invent 3 new holidays tailored for chronic introverts.",
  },
  {
    icon: <Zap className="w-4 h-4" />,
    color: "yellow",
    text: "What's my most useless but cool-sounding secret agent gadget?",
  },
] as const;

export const COLOR_MAP: Record<ColorName, { bg: string; border: string; icon: string; glow: string }> = {
  emerald: {
    bg: "hover:bg-emerald-500/5",
    border: "hover:border-emerald-500/30",
    icon: "text-emerald-400",
    glow: "group-hover:shadow-emerald-500/50",
  },
  orange: {
    bg: "hover:bg-orange-500/5",
    border: "hover:border-orange-500/30",
    icon: "text-orange-400",
    glow: "group-hover:shadow-orange-500/50",
  },
  blue: {
    bg: "hover:bg-blue-500/5",
    border: "hover:border-blue-500/30",
    icon: "text-blue-400",
    glow: "group-hover:shadow-blue-500/50",
  },
  purple: {
    bg: "hover:bg-purple-500/5",
    border: "hover:border-purple-500/30",
    icon: "text-purple-400",
    glow: "group-hover:shadow-purple-500/50",
  },
  pink: {
    bg: "hover:bg-pink-500/5",
    border: "hover:border-pink-500/30",
    icon: "text-pink-400",
    glow: "group-hover:shadow-pink-500/50",
  },
  cyan: {
    bg: "hover:bg-cyan-500/5",
    border: "hover:border-cyan-500/30",
    icon: "text-cyan-400",
    glow: "group-hover:shadow-cyan-500/50",
  },
  amber: {
    bg: "hover:bg-amber-500/5",
    border: "hover:border-amber-500/30",
    icon: "text-amber-400",
    glow: "group-hover:shadow-amber-500/50",
  },
  rose: {
    bg: "hover:bg-rose-500/5",
    border: "hover:border-rose-500/30",
    icon: "text-rose-400",
    glow: "group-hover:shadow-rose-500/50",
  },
  teal: {
    bg: "hover:bg-teal-500/5",
    border: "hover:border-teal-500/30",
    icon: "text-teal-400",
    glow: "group-hover:shadow-teal-500/50",
  },
  yellow: {
    bg: "hover:bg-yellow-500/5",
    border: "hover:border-yellow-500/30",
    icon: "text-yellow-400",
    glow: "group-hover:shadow-yellow-500/50",
  },
};
