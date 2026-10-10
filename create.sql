DROP TABLE IF EXISTS ItemCategories;
DROP TABLE IF EXISTS Bids;
DROP TABLE IF EXISTS Items;
DROP TABLE IF EXISTS Categories;
DROP TABLE IF EXISTS Users;

CREATE TABLE Users (
    UserID TEXT NOT NULL PRIMARY KEY,
    Rating INT NOT NULL,
    Location TEXT,
    Country TEXT
);

CREATE TABLE Categories (
    Category_Name TEXT NOT NULL PRIMARY KEY
);

CREATE TABLE Items (
    ItemID INT NOT NULL PRIMARY KEY,
    UserID TEXT NOT NULL,
    Name TEXT NOT NULL,
    Currently REAL NOT NULL,
    Buy_Price REAL,
    First_Bid REAL NOT NULL,
    Number_of_Bids INT NOT NULL,
    Started TEXT NOT NULL,
    Ends TEXT NOT NULL,
    Description TEXT,
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE Bids (
    BidID INT NOT NULL PRIMARY KEY,
    ItemID INT NOT NULL,
    UserID TEXT NOT NULL,
    Time TEXT NOT NULL,
    Amount REAL NOT NULL,
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
    FOREIGN KEY (UserID) REFERENCES Users(UserID)
);

CREATE TABLE ItemCategories (
    ItemID INT NOT NULL,
    Category_Name TEXT NOT NULL,
    PRIMARY KEY (ItemID, Category_Name),
    FOREIGN KEY (ItemID) REFERENCES Items(ItemID),
    FOREIGN KEY (Category_Name) REFERENCES Categories(Category_Name)
);
