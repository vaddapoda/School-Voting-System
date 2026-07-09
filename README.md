# Student Council Election Management System

A desktop-based election management application built using Python and Tkinter as a Class 12 Computer Science project.

The application helps manage student council elections by handling voters, nominees, voting, results, and CSV exports in one system.

## Features

- Admin login and password management
- Add, edit, delete, and filter voter records
- Add, edit, delete, and filter nominee records
- Import voter details from a CSV file
- Class, section, name, and house-based voting flow
- Prevents students from voting more than once
- Supports school-level and house-level positions
- Displays winners in table format
- Displays winners in a printable format
- Exports winner details to a CSV file
- Uses a local SQLite database

## Technologies Used

- Python
- Tkinter and ttk
- SQLite
- CSV module

## Project Structure

```text
School-Voting-System/
├── main.py
├── passwords.txt
└── README.md
```

## Requirements

- Python 3.10 or later
- Tkinter, included with most Python installations

## How to Run

1. Download or clone this repository.
2. Open Terminal in the project folder.
3. Run:

```bash
python main.py
```

The SQLite database is created automatically when the application is run.

## Default Passwords

The project includes default passwords so it can be tested immediately.

| Access | Default Password |
| --- | --- |
| Admin Panel | `ADMIN` |
| Exit Voting Mode | `EXIT` |

Passwords can be changed later from the **Change Passwords** option in the Admin Panel.

## Data Privacy

This repository does not include real student information or actual election data.

Any data used for testing or demonstration should be fictional.

## Screenshots

### Main Menu

<p align="center">
  <img src="screenshots/main-menu.png" width="700">
</p>

### Admin Panel

<p align="center">
  <img src="screenshots/admin-panel.png" width="700">
</p>

## Winners

<table>
  <tr>
    <td align="center">
      <b>Printable Winners View</b><br><br>
      <img src="screenshots/winners-printable.png" width="500">
    </td>
    <td align="center">
      <b>Table Winners View</b><br><br>
      <img src="screenshots/winners-table.png" width="500">
    </td>
  </tr>
</table>

## Author

Created by `Gautam A` as a Class 12 Computer Science project.
