import {
  Book,
  Brain,
  Calendar,
  Camera,
  Coffee,
  Dumbbell,
  FileText,
  Film,
  Gamepad2,
  Gift,
  Globe,
  Heart,
  House,
  Leaf,
  Lightbulb,
  Mail,
  MapPin,
  Moon,
  Music,
  Palette,
  Plane,
  Search,
  ShoppingBag,
  Sparkles,
  Star,
  Sun,
  Utensils,
} from "lucide-react";

import type { ColorName } from "./types";

export const ALL_QUICK_STARTS = [
  {
    icon: <Utensils className="w-4 h-4" />,
    color: "orange",
    text: "Suggest a simple brunch recipe that feels special and Instagram-worthy.",
  },
  {
    icon: <Globe className="w-4 h-4" />,
    color: "blue",
    text: "Search for hidden gems and underrated neighborhoods to explore in Tokyo.",
  },
  {
    icon: <Heart className="w-4 h-4" />,
    color: "rose",
    text: "What are some creative but affordable Valentine's Day gift ideas?",
  },
  {
    icon: <Star className="w-4 h-4" />,
    color: "amber",
    text: "What movies are coming out this year? Help me create a must-watch list.",
  },
  {
    icon: <Coffee className="w-4 h-4" />,
    color: "yellow",
    text: "Recommend some creative coffee drinks I can make at home.",
  },
  {
    icon: <MapPin className="w-4 h-4" />,
    color: "emerald",
    text: "I want to go camping solo this weekend. Any beginner-friendly spots?",
  },
  {
    icon: <Music className="w-4 h-4" />,
    color: "purple",
    text: "Find me some chill Lofi playlists perfect for late night vibes.",
  },
  {
    icon: <Gift className="w-4 h-4" />,
    color: "pink",
    text: "My friend's birthday is coming up. What can I get for under $30?",
  },
  {
    icon: <Sun className="w-4 h-4" />,
    color: "orange",
    text: "Where are the best flower fields for a spring photo shoot?",
  },
  {
    icon: <Moon className="w-4 h-4" />,
    color: "cyan",
    text: "I can't sleep at night. What are some science-backed tips for better sleep?",
  },
  {
    icon: <Plane className="w-4 h-4" />,
    color: "blue",
    text: "First time going to Thailand! Help me plan what to prepare.",
  },
  {
    icon: <Book className="w-4 h-4" />,
    color: "teal",
    text: "Recommend some addictive mystery novels I won't be able to put down.",
  },
  {
    icon: <Gamepad2 className="w-4 h-4" />,
    color: "purple",
    text: "What are the best Nintendo Switch games to play in 2025?",
  },
  {
    icon: <Palette className="w-4 h-4" />,
    color: "pink",
    text: "I want to learn to draw but I'm a total beginner. Where do I start?",
  },
  {
    icon: <ShoppingBag className="w-4 h-4" />,
    color: "rose",
    text: "Spring is here! What fashion trends are in style this season?",
  },
  {
    icon: <Leaf className="w-4 h-4" />,
    color: "emerald",
    text: "What houseplants are easy to care for and look aesthetic?",
  },
  {
    icon: <Film className="w-4 h-4" />,
    color: "amber",
    text: "Find me the funniest comedy movies for a movie night with friends.",
  },
  {
    icon: <Dumbbell className="w-4 h-4" />,
    color: "orange",
    text: "Quick stretching exercises office workers can do during breaks?",
  },
  {
    icon: <Brain className="w-4 h-4" />,
    color: "cyan",
    text: "Share some fun psychology facts I can post on social media.",
  },
  {
    icon: <Lightbulb className="w-4 h-4" />,
    color: "yellow",
    text: "Life feels boring. What are some unique hobbies I could pick up?",
  },
  {
    icon: <Camera className="w-4 h-4" />,
    color: "teal",
    text: "What phone photography tips make photos look more professional?",
  },
  {
    icon: <Calendar className="w-4 h-4" />,
    color: "blue",
    text: "How can I scientifically plan my week to be more productive?",
  },
  {
    icon: <House className="w-4 h-4" />,
    color: "purple",
    text: "Budget-friendly tips to make a rented apartment look amazing?",
  },
  {
    icon: <Sparkles className="w-4 h-4" />,
    color: "pink",
    text: "What's a simple skincare routine for someone who's too lazy?",
  },
  {
    icon: <Mail className="w-4 h-4" />,
    color: "emerald",
    text: "Long distance relationship tips? Give me some romantic ideas!",
  },
  {
    icon: <Search className="w-4 h-4" />,
    color: "amber",
    text: "What are the hottest restaurants trending on social media right now?",
  },
  {
    icon: <FileText className="w-4 h-4" />,
    color: "cyan",
    text: "I want to start journaling but don't know what to write. Give me prompts!",
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
