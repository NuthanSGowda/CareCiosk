-- Drop existing users table to reset
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS users;

-- Create users table with plain-text password
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('user', 'admin') DEFAULT 'user'
);

-- Create orders table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    medicines JSON NOT NULL,
    total DECIMAL(10, 2) NOT NULL,
    order_date DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Insert sample admin user (username: admin, password: admin123)
INSERT INTO users (username, password, role) VALUES
    ('admin', 'admin123', 'admin');

-- Insert sample regular user (username: user1, password: user123)
INSERT INTO users (username, password, role) VALUES
    ('user1', 'user123', 'user');
    