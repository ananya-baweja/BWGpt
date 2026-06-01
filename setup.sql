USE MockCorpDB;
GO

CREATE TABLE Departments (
    DepartmentID INT PRIMARY KEY,
    DepartmentName NVARCHAR(100),
    AnnualBudget DECIMAL(18,2)
);
GO

CREATE TABLE Transactions (
    TransactionID INT PRIMARY KEY,
    DepartmentID INT,
    Amount DECIMAL(18,2),
    TransactionDate DATE,
    VendorName NVARCHAR(100)
);
GO

INSERT INTO Departments VALUES
(1,'IT',1000000),
(2,'HR',500000),
(3,'Finance',750000);
GO

INSERT INTO Transactions VALUES
(1,1,12000,'2026-01-15','Microsoft'),
(2,1,5000,'2026-02-10','AWS'),
(3,2,3000,'2026-03-01','LinkedIn'),
(4,3,8000,'2026-03-15','Oracle');
GO
