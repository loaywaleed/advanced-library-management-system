# Checklist

### Advanced Library Management System Checklist

### Project Idea

- [x]  Build a library management system to manage libraries, books, authors, and categories
- [x]  Implement user registration, login, and password recovery
- [x]  Allow users to borrow and return multiple books in one transaction
- [x]  Provide notifications and real-time updates for book availability

### Must-Have Endpoints

**Library Management**

- [x]  Create endpoint to list libraries
- [x]  Implement filtering of libraries by book categories and authors
- [x]  Calculate distances between users and nearby libraries

**Authors**

- [x]  Create endpoint to list authors with their book counts
- [x]  Implement filtering by library and book category (update book counts with filters)

**Books**

- [x]  Create endpoint to list books
- [x]  Implement filtering by category, library, and author
- [x]  Return author and category names in book endpoint responses

**Loaded Authors Endpoint**

- [x]  Create endpoint to list authors with all their book objects
- [x]  Include category object for each book
- [x]  Implement filtering by category and library

### Task Details

**1. Notifications**

- [x]  Email Notifications:
    - [x]  Send confirmation emails upon borrowing
    - [x]  Test email notifications locally using Mailhog (no actual email service like AWS SES or Sendmail)
    - [x]  Send daily reminder emails during the last 3 days of the borrowing period

**2. Business Logic**

- [x]  Borrowing Rules:
    - [x]  Allow borrowing up to 3 books; require returning one to borrow a 4th
    - [x]  Require users to specify a return date (maximum 1 month)
    - [x]  Implement daily penalty for late returns
- [x]  Penalty Calculation:
    - [x]  Calculate penalties based on overdue days

**3. Nice to Have**

- [x]  Implement user roles and permissions
- [x]  Apply rate limiting to API endpoints
- [x]  Use Celery (or an alternative) for email sending task queue
- [x]  Containerize the project using Docker
- [ ]  Deploy the project on the free AWS tier
- [ ]  Implement caching for frequently accessed data
- [ ]  Real-time Notifications:
    - [ ]  Use WebSockets (Django Channels) to notify when a book is returned and available
- [ ]  Manage multiple library branches with unique locations
- [ ]  Support multiple languages (internationalization)
