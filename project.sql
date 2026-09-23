create database if not exists ecommerce_db;
use ecommerce_db;
#-------------user table-------------------
create table if not exists users(
id int auto_increment primary key,
name varchar(100) not null,
email varchar(120) not null unique,
password_hash varchar(64) not null,
role enum('customer','admin') default 'customer',
created_at timestamp default current_timestamp

);
#----------------product_table-------------------
create table if not exists products(
id int auto_increment primary key,
name varchar(150) not null,
category varchar(80) not null,
price decimal(10,2) not null,
stock int not null default 0
);
#----------------cart_table------------------------
create table if not exists cart_items(
id int auto_increment primary key,
user_id int not null,
product_id int not null,
quantity int not null default 1,
foreign key(user_id)references users(id) on delete cascade,
foreign key (product_id) references products(id) ON delete cascade,
unique key unique_user_products(user_id,product_id)
);
#---------------order_table-------------------------
create table if not exists orders(
id int auto_increment primary key,
user_id int not null,
total_amount decimal(10,2),
status enum('pending','paid','delivered')default 'paid',
delivery_address text not null,
created_at timestamp default current_timestamp,
foreign key(user_id) references users(id) on delete cascade
);


#--------------- Order_Items_table-----------------------------------------
create table if not exists order_items (
    id int auto_increment primary key,
    order_id int not null,
    product_id int not null,
    quantity int not null,
    price decimal(10, 2) not null,
    foreign key(order_id) references orders(id) on delete cascade,
    foreign key (product_id) references products(id) on delete restrict
);

#--------- Initial catalog data-------------------------------------
INSERT IGNORE INTO products (id, name, category, price, stock) VALUES 
(1, 'Mechanical Keyboard', 'Electronics', 3499.00, 15),
(2, 'Gaming Mouse', 'Electronics', 1299.00, 25),
(3, 'Noise-Cancelling Headphones', 'Audio', 4999.00, 10),
(4, 'Laptop Stand', 'Accessories', 899.00, 30);

select * from products;
 
insert ignore into users (name,email,password_hash) values
('Rahim','rahim@gmail.com','abcde'),
('Shajaha','shajaha@gmail.com','prince'),
('Akbar','akbar@gmail.com','king'),
('Birbal','birbal@gmail.com','wazir');
select * from users;

select*from cart_items;



