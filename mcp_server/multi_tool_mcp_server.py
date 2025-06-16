#!/usr/bin/env python3
"""
Multi-tool MCP Server with various utility functions
"""

import asyncio
import json
import random
import math
from datetime import datetime
from typing import Dict, Any, List

from mcp.server import FastMCP

# Initialize MCP server
mcp = FastMCP("Multi-Tool Server")

# Sample data for tools
QUOTES = [
    "The only way to do great work is to love what you do. - Steve Jobs",
    "Innovation distinguishes between a leader and a follower. - Steve Jobs",
    "Life is what happens to you while you're busy making other plans. - John Lennon",
    "The future belongs to those who believe in the beauty of their dreams. - Eleanor Roosevelt",
    "It is during our darkest moments that we must focus to see the light. - Aristotle",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. - Winston Churchill",
    "The only impossible journey is the one you never begin. - Tony Robbins"
]

WEATHER_DATA = {
    "New York": {"temp": 22, "condition": "Sunny", "humidity": 65},
    "London": {"temp": 15, "condition": "Cloudy", "humidity": 78},
    "Tokyo": {"temp": 28, "condition": "Partly Cloudy", "humidity": 70},
    "Sydney": {"temp": 25, "condition": "Rainy", "humidity": 85},
    "Paris": {"temp": 18, "condition": "Overcast", "humidity": 72}
}

@mcp.tool()
def calculate_bmi(weight: float, height: float) -> Dict[str, Any]:
    """
    Calculate Body Mass Index (BMI) from weight and height.
    
    Args:
        weight: Weight in kilograms
        height: Height in meters
    
    Returns:
        Dictionary with BMI value and category
    """
    if weight <= 0 or height <= 0:
        return {"error": "Weight and height must be positive values"}
    
    bmi = weight / (height ** 2)
    
    if bmi < 18.5:
        category = "Underweight"
    elif bmi < 25:
        category = "Normal weight"
    elif bmi < 30:
        category = "Overweight"
    else:
        category = "Obese"
    
    return {
        "bmi": round(bmi, 2),
        "category": category,
        "weight": weight,
        "height": height
    }

@mcp.tool()
def get_weather(city: str = "New York") -> Dict[str, Any]:
    """
    Get weather information for a specified city.
    
    Args:
        city: Name of the city (default: New York)
    
    Returns:
        Dictionary with weather information
    """
    city_title = city.title()
    
    if city_title in WEATHER_DATA:
        weather = WEATHER_DATA[city_title].copy()
        weather["city"] = city_title
        weather["timestamp"] = datetime.now().isoformat()
        return weather
    else:
        # Return random weather data for unknown cities
        return {
            "city": city_title,
            "temp": random.randint(10, 35),
            "condition": random.choice(["Sunny", "Cloudy", "Rainy", "Partly Cloudy", "Overcast"]),
            "humidity": random.randint(40, 90),
            "timestamp": datetime.now().isoformat(),
            "note": "Simulated data for unknown city"
        }

@mcp.tool()
def get_random_quote() -> Dict[str, str]:
    """
    Get a random inspirational quote.
    
    Returns:
        Dictionary with a random quote
    """
    quote = random.choice(QUOTES)
    return {
        "quote": quote,
        "timestamp": datetime.now().isoformat()
    }

@mcp.tool()
def calculate_compound_interest(principal: float, rate: float, time: float, compound_frequency: int = 1) -> Dict[str, Any]:
    """
    Calculate compound interest.
    
    Args:
        principal: Initial amount
        rate: Annual interest rate (as percentage)
        time: Time period in years
        compound_frequency: Number of times interest is compounded per year (default: 1)
    
    Returns:
        Dictionary with compound interest calculation results
    """
    if principal <= 0 or rate < 0 or time < 0 or compound_frequency <= 0:
        return {"error": "Invalid input values"}
    
    rate_decimal = rate / 100
    amount = principal * (1 + rate_decimal / compound_frequency) ** (compound_frequency * time)
    interest = amount - principal
    
    return {
        "principal": principal,
        "rate": rate,
        "time": time,
        "compound_frequency": compound_frequency,
        "final_amount": round(amount, 2),
        "interest_earned": round(interest, 2)
    }

@mcp.tool()
def generate_password(length: int = 12, include_symbols: bool = True) -> Dict[str, str]:
    """
    Generate a random password.
    
    Args:
        length: Length of the password (default: 12)
        include_symbols: Whether to include symbols (default: True)
    
    Returns:
        Dictionary with generated password
    """
    import string
    
    if length < 4:
        return {"error": "Password length must be at least 4 characters"}
    
    characters = string.ascii_letters + string.digits
    if include_symbols:
        characters += "!@#$%^&*"
    
    password = ''.join(random.choice(characters) for _ in range(length))
    
    return {
        "password": password,
        "length": length,
        "includes_symbols": include_symbols,
        "strength": "Strong" if length >= 12 else "Medium" if length >= 8 else "Weak"
    }

@mcp.tool()
def convert_temperature(temperature: float, from_unit: str, to_unit: str) -> Dict[str, Any]:
    """
    Convert temperature between Celsius, Fahrenheit, and Kelvin.
    
    Args:
        temperature: Temperature value
        from_unit: Source unit (C, F, or K)
        to_unit: Target unit (C, F, or K)
    
    Returns:
        Dictionary with converted temperature
    """
    from_unit = from_unit.upper()
    to_unit = to_unit.upper()
    
    valid_units = ['C', 'F', 'K']
    if from_unit not in valid_units or to_unit not in valid_units:
        return {"error": "Units must be C (Celsius), F (Fahrenheit), or K (Kelvin)"}
    
    # Convert to Celsius first
    if from_unit == 'F':
        celsius = (temperature - 32) * 5/9
    elif from_unit == 'K':
        celsius = temperature - 273.15
    else:
        celsius = temperature
    
    # Convert from Celsius to target unit
    if to_unit == 'F':
        result = celsius * 9/5 + 32
    elif to_unit == 'K':
        result = celsius + 273.15
    else:
        result = celsius
    
    return {
        "original_temperature": temperature,
        "original_unit": from_unit,
        "converted_temperature": round(result, 2),
        "converted_unit": to_unit
    }

@mcp.tool()
def calculate_tip(bill_amount: float, tip_percentage: float = 15.0, num_people: int = 1) -> Dict[str, Any]:
    """
    Calculate tip and split bill among people.
    
    Args:
        bill_amount: Total bill amount
        tip_percentage: Tip percentage (default: 15%)
        num_people: Number of people to split the bill (default: 1)
    
    Returns:
        Dictionary with tip calculation and bill splitting
    """
    if bill_amount <= 0 or tip_percentage < 0 or num_people <= 0:
        return {"error": "Invalid input values"}
    
    tip_amount = bill_amount * (tip_percentage / 100)
    total_amount = bill_amount + tip_amount
    per_person = total_amount / num_people
    
    return {
        "bill_amount": bill_amount,
        "tip_percentage": tip_percentage,
        "tip_amount": round(tip_amount, 2),
        "total_amount": round(total_amount, 2),
        "num_people": num_people,
        "per_person": round(per_person, 2)
    }

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
