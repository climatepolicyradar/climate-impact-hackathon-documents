# Climate Policy Radar Hackathon Challenge Documentation

Welcome to the Climate Policy Radar (CPR) Hackathon Challenge! This repository contains essential documentation and resources to help you create innovative solutions that make climate law and policy information more accessible and actionable.

Please note, these documents are work in progress. While we have tried to be complete and correct, there may be mistakes or omissions. Please let us know via issues on this repository.

## Table of Contents

- API Documentation
- Taxonomy Reference
- Dataset Access
- Principles: Accessibility Guidelines and responsible AI Checklist
- Tutorial

## API Documentation

In the `api-docs.md` file, you'll find comprehensive documentation for the Climate Policy Radar search API. The search API allows you to query the full CPR document dataset using semantic search. The results will include details of which specific passages matched the search query.

The documentation includes:

- How to call the API
- Response structures and data schemas
- Code snippets and examples for Python

## Taxonomy Reference

Our data uses defined taxonomies for entities such as countries. To query the API, you will need to use these values, which can be found in the `reference-values.md` file.

## Dataset Access

We also have several datasets that you can use: our extensive climate law and policy text database, and a dataset of climate policy targets extracted from. In the `datasets` directory you'll find instructions on how to access each dataset.

You should use these datasets over the search API when you want to do more thorough or intensive tasks or processing, as the search API will limit how many results you can get.

## Principles: Accessibility Guidelines and responsible AI Checklist

Accessibility is a key consideration for this hackathon. In the `principles.md` file, you'll find a set of best practices and guidelines for designing user interfaces and presenting complex information to users with diverse language proficiencies and comprehension levels. Refer to these guidelines to ensure your solutions are inclusive and user-friendly.

As you develop your solutions using generative AI techniques, it's crucial to consider the limitations and potential risks. The `principles.md` file also contains a checklist of best practices for mitigating issues such as hallucinations, biases, and misleading outputs. Use this checklist to ensure your solutions are reliable, transparent, and ethically sound.

## Technical Tutorial

To help you get started quickly, we've prepared a brief technical tutorial in the `python-tutorial.ipynb` notebook. This tutorial covers various aspects of working with the Climate Policy Radar API.

---

We're excited to see the innovative solutions you'll create during this hackathon. If you have any questions or need further assistance, don't hesitate to reach out to the event organizers. Happy hacking!
