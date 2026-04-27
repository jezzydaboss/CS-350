# CS-350

Summarize the project and what problem it was solving.
What did you do particularly well?
Where could you improve?
What tools and/or resources are you adding to your support network?
What skills from this project will be particularly transferable to other projects and/or course work?
How did you make this project maintainable, readable, and adaptable?


Project Summary and Problem Solved

The goal of this project was to design and prototype a Smart Thermostat System for SysTec, bridging the gap between physical environmental sensing and cloud-ready data logging. The project addressed the challenge of creating a reliable embedded system that accurately reads ambient temperature via the I2C protocol, manages distinct operational states (Off, Heat, and Cool), and provides real-time visual feedback to the user through PWM-controlled LEDs and an LCD. By simulating data transmission over UART, the prototype successfully demonstrated how a local hardware device can integrate into a larger server-side analytics infrastructure.

Technical Excellence and Maintainability

The project was particularly successful in its implementation of a formal State Machine architecture, which ensured the system transitioned cleanly between modes without the logic errors common in simple conditional loops. To ensure the code was maintainable and readable, I utilized modular programming and clear naming conventions, allowing the hardware pins and logic thresholds to be updated with minimal effort. By utilizing hardware interrupts for button presses, the thermostat remains highly responsive, processing user temperature adjustments immediately without interrupting the primary sensor-reading and display cycles.

Growth and Future Application

This project significantly expanded my professional support network to include manufacturer data sheets and technical hardware documentation as primary resources, moving beyond basic tutorials. I identified room for future improvement in implementing hysteresis to prevent rapid system cycling and more advanced hardware debouncing for the physical buttons. The skills gained—specifically in asynchronous threading, I2C communication, and cross-architecture analysis—are directly transferable to future engineering work in automotive systems, IoT development, and embedded computer engineering.
