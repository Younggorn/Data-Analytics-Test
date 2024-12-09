import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from dateutil.relativedelta import relativedelta


# Page Configuration
st.set_page_config(page_title="Restaurant Dashboard", layout="wide")
st.title("Restaurant Performance Dashboard")

# Load Data
data = pd.read_csv('test_data.csv')

# Data Preprocessing
## Convert date columns to datetime
data['Date'] = pd.to_datetime(data['Date'], errors='coerce')
data['Order Time'] = pd.to_datetime(data['Order Time'], errors='coerce')
data['Serve Time'] = pd.to_datetime(data['Serve Time'], errors='coerce')

## Add Day of Week column
data['Day of Week'] = data['Date'].dt.day_name()

## Calculate additional columns
data['Wait Time (minutes)'] = (data['Serve Time'] - data['Order Time']).dt.total_seconds() / 60

## Filter out invalid dates
data = data.dropna(subset=['Date'])

## Extract Month, Year, and Day
data['Month'] = data['Date'].dt.month
data['Year'] = data['Date'].dt.year
data['Day'] = data['Date'].dt.day

# Grouping Data
## Group data by Day of Week
sales_by_day = data.groupby('Day of Week').size().reset_index(name='Total Sales')

## Sort the days of the week
days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
sales_by_day['Day of Week'] = pd.Categorical(sales_by_day['Day of Week'], categories=days_order, ordered=True)
sales_by_day = sales_by_day.sort_values('Day of Week')

# Sidebar Filters
st.sidebar.header("Filters")
category_filter = st.sidebar.multiselect("Select Category", data['Category'].unique(), default=data['Category'].unique())
date_filter = st.sidebar.date_input("Select Date Range", [data['Date'].min().date(), data['Date'].max().date()])


date_filter = pd.to_datetime(date_filter)


filtered_data = data[
    (data['Category'].isin(category_filter)) &
    (data['Date'] >= date_filter[0]) &
    (data['Date'] <= date_filter[1])
]


sales_by_day_category = (
    filtered_data.groupby(['Day of Week', 'Category']).size().reset_index(name='Total Sales')
)


sales_by_day_category['Day of Week'] = pd.Categorical(
    sales_by_day_category['Day of Week'], categories=days_order, ordered=True
)
sales_by_day_category = sales_by_day_category.sort_values('Day of Week')


# KPI Calculation

## 1. Total Sales (Menu Count)
total_sales = data['Menu'].count()  # Assuming 'Menu' column contains the menu sold

## 2. Total Revenue (Price)
total_revenue = data['Price'].sum()  # Assuming 'Price' column contains revenue per order

## 3. Average Service Time (Serve Time - Order Time)
average_service_time = (data['Serve Time'] - data['Order Time']).dt.total_seconds().mean() / 60

## 4. Data Range (First Date - Last Date)
data_start_date = data['Date'].min().date()
data_end_date = data['Date'].max().date()

# Calculate the difference in months and days
date_difference = relativedelta(data_end_date, data_start_date)
data_range = f"{date_difference.years * 12 + date_difference.months} เดือน {date_difference.days} วัน"

# Display KPIs in Columns
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(label="Total Sales (Menu)", value=f"{total_sales:,}")

with col2:
    st.metric(label="Total Revenue (Price)", value=f"${total_revenue:,.2f}")

with col3:
    st.metric(label="Avg Service Time (minutes)", value=f"{average_service_time:.2f} min")

with col4:
    st.metric(label="Data Range", value=data_range)



st.markdown(
    """
    <div style="text-align: center;">
        <strong>รายได้เปรียบเทียบแต่ละเดือน</strong>
    </div>
    """,
    unsafe_allow_html=True
    )


filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.to_period('M').astype(str)


total_revenue = filtered_data.groupby('Month')['Price'].sum().reset_index(name='Total Revenue')
drink_revenue = filtered_data[filtered_data['Category'] == 'drink'].groupby('Month')['Price'].sum().reset_index(name='Drink Revenue')
food_revenue = filtered_data[filtered_data['Category'] == 'food'].groupby('Month')['Price'].sum().reset_index(name='Food Revenue')


revenue_data = total_revenue.merge(drink_revenue, on='Month', how='left').merge(food_revenue, on='Month', how='left')


fig = px.line(
    revenue_data,
    x='Month',
    y=['Total Revenue', 'Drink Revenue', 'Food Revenue'],
    markers=True,
    labels={'value': 'Revenue (in $)', 'variable': 'Revenue Type', 'Month': 'Month'},
    title="Monthly Revenue: Total, Drink, and Food"
)


st.plotly_chart(fig)


col1, col2 = st.columns(2)


with col1:
    st.markdown(
    """
    <div style="text-align: center;">
        <strong>กราฟแสดงยอดการขายในแต่ละวัน</strong>
    </div>
    """,
    unsafe_allow_html=True
)
    # สร้างกราฟแท่งด้วย Plotly Express
    fig = px.bar(
        sales_by_day_category,
        x='Day of Week',
        y='Total Sales',
        color='Category',  # แยกสีตาม Category
        labels={'Total Sales': 'Total Sales', 'Day of Week': 'Day of Week'},  # ตั้งชื่อแกน
        title="Total Sales by Day of Week",  # ชื่อกราฟ
        height=400,  # ความสูงของกราฟ
        template="plotly_white"  # ธีมของกราฟ
    )

    # แสดงกราฟใน Streamlit
    st.plotly_chart(fig)
with col2:
    st.markdown(
    """
    <div style="text-align: center;">
        <strong>กราฟแสดงยอดการขายในแต่ละเดือน</strong>
    </div>
    """,
    unsafe_allow_html=True
    )
    

    
    filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.to_period('M').astype(str)
    monthly_sales = filtered_data.groupby(['Month', 'Category'])['Menu'].count().reset_index()
    monthly_sales.columns = ['Month', 'Category', 'Total Orders']

   
    fig = px.bar(
        monthly_sales,
        x='Month',
        y='Total Orders',
        color='Category',  
        labels={'Total Orders': 'Total Orders', 'Month': 'Month'},  
        title="Monthly Sales (by Category)",  
        height=400  
    )

    
    st.plotly_chart(fig)



col1 ,col2 =st.columns(2)

with col1:
    st.markdown(
    """
    <div style="text-align: center;">
        <strong>เมนูยอดนิยม</strong>
    </div>
    """,
    unsafe_allow_html=True
)
    # สร้างตัวเลือกกราฟ
    options = ['ทั้งหมด', 'อาหาร', 'น้ำ']

    # Dropdown เมนู
    selected_chart = st.selectbox("", options)

    # สร้างฟังก์ชันสำหรับแต่ละกราฟ
    def one():
        
        
            # นับจำนวนเมนูทั้งหมดและเรียงลำดับจากมากไปน้อย
        menu_sales = filtered_data.groupby('Menu')['Menu'].count().reset_index(name='Total Orders')
        menu_sales = menu_sales.sort_values(by='Total Orders', ascending=False)

        # เตรียมข้อมูลสำหรับแกน X และ Y
        x = menu_sales['Menu']
        y = menu_sales['Total Orders']

        # สร้างกราฟ
        fig = go.Figure(data=[go.Bar(
            x=x,
            y=y,
            text=y,  # แสดงค่าบนแท่งกราฟ
            textposition='auto'  # ตำแหน่งของข้อความ
        )])

        # ตั้งค่าชื่อกราฟและแกน
        fig.update_layout(
            
            xaxis_title="Menu",
            yaxis_title="Total Orders",
            template="plotly_white"
        )

        # แสดงกราฟใน Streamlit
        st.plotly_chart(fig)

    def two():
                        # กรองเฉพาะ Category = food
        food_data = filtered_data[filtered_data['Category'] == 'food']

        # นับจำนวนเมนูทั้งหมดและเรียงลำดับจากมากไปน้อย
        menu_sales = food_data.groupby('Menu')['Menu'].count().reset_index(name='Total Orders')
        menu_sales = menu_sales.sort_values(by='Total Orders', ascending=False)

        # เตรียมข้อมูลสำหรับแกน X และ Y
        x = menu_sales['Menu']
        y = menu_sales['Total Orders']

        # สร้างกราฟ
        fig = go.Figure(data=[go.Bar(
            x=x,
            y=y,
            text=y,  # แสดงค่าบนแท่งกราฟ
            textposition='auto'  # ตำแหน่งของข้อความ
        )])

        # ตั้งค่าชื่อกราฟและแกน
        fig.update_layout(
            
            xaxis_title="Menu",
            yaxis_title="Total Orders",
            template="plotly_white"
        )

        # แสดงกราฟใน Streamlit
        st.plotly_chart(fig)

                        

    def three():
        # กรองเฉพาะ Category = food
        food_data = filtered_data[filtered_data['Category'] == 'drink']

        # นับจำนวนเมนูทั้งหมดและเรียงลำดับจากมากไปน้อย
        menu_sales = food_data.groupby('Menu')['Menu'].count().reset_index(name='Total Orders')
        menu_sales = menu_sales.sort_values(by='Total Orders', ascending=False)

        # เตรียมข้อมูลสำหรับแกน X และ Y
        x = menu_sales['Menu']
        y = menu_sales['Total Orders']

        # สร้างกราฟ
        fig = go.Figure(data=[go.Bar(
            x=x,
            y=y,
            text=y,  # แสดงค่าบนแท่งกราฟ
            textposition='auto'  # ตำแหน่งของข้อความ
        )])

        # ตั้งค่าชื่อกราฟและแกน
        fig.update_layout(
            
            xaxis_title="Menu",
            yaxis_title="Total Orders",
            template="plotly_white"
        )

        # แสดงกราฟใน Streamlit
        st.plotly_chart(fig)


    # แสดงกราฟตามตัวเลือก
    if selected_chart == 'ทั้งหมด':
        one()
    elif selected_chart == 'อาหาร':
        two()
    elif selected_chart == 'น้ำ':
        three()

with col2:
    st.markdown(
    """
    <div style="text-align: center;">
        <strong>Drinks Staff</strong>
    </div>
    """,
    unsafe_allow_html=True
    )
    # สร้างตัวเลือกกราฟ
    options = ['กราฟแสดงการเปรียบเทียบจำนวน Drinks Staff กับ ยอดขายทั้งหมด', 'กราฟแสดงการเปรียบเทียบจำนวน Drinks Staff กับ ยอดขายในแต่ละวัน']

    # Dropdown เมนู
    selected_chart = st.selectbox("", options)

    # สร้างฟังก์ชันสำหรับแต่ละกราฟ
    def one():
            # นับจำนวน Menu ตาม Drinks Staff และ Category
        staff_sales = filtered_data.groupby(['Drinks Staff', 'Category'])['Menu'].count().reset_index()
        staff_sales.columns = ['Drinks Staff', 'Category', 'Total Orders']

        # สร้างกราฟแท่งด้วย Plotly Express
        fig = px.bar(
            staff_sales,
            x='Drinks Staff',
            y='Total Orders',
            color='Category',  # แยกสีตาม Category
            barmode='group',   # แสดงกราฟในรูปแบบกลุ่ม
            labels={
                'Drinks Staff': 'Number of Drinks Staff',
                'Total Orders': 'Total Orders',
                'Category': 'Category'
            },
            title="Total Orders by Drinks Staff and Category",
            template="plotly_white",
            height=400
        )

        # แสดงกราฟใน Streamlit
        st.plotly_chart(fig)

    def two():
                # สมมติว่าคุณมี DataFrame ชื่อ filtered_data และมีคอลัมน์ 'Drinks Staff', 'Menu', และ 'Day of Week'
        filtered_data = data[
    (data['Category'].isin(category_filter)) &
    (data['Date'] >= date_filter[0]) &
    (data['Date'] <= date_filter[1])


]

        # นับจำนวนเมนูตามวันและจำนวนคน
        daily_sales = filtered_data.groupby(['Day of Week', 'Drinks Staff'])['Menu'].count().reset_index()
        daily_sales.columns = ['Day of Week', 'Drinks Staff', 'Total Orders']

        # ลำดับวันในสัปดาห์
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        daily_sales['Day of Week'] = pd.Categorical(daily_sales['Day of Week'], categories=day_order, ordered=True)

        # เตรียมข้อมูลสำหรับ Plotly
        fig = go.Figure()

        # สร้างแท่งกราฟสำหรับแต่ละจำนวนคน (Drinks Staff)
        for staff in daily_sales['Drinks Staff'].unique():
            filtered_data = daily_sales[daily_sales['Drinks Staff'] == staff]
            fig.add_trace(
                go.Bar(
                    x=filtered_data['Day of Week'],
                    y=filtered_data['Total Orders'],
                    name=f"Drinks Staff {staff}"
                )
            )

        # ปรับแต่งกราฟ
        fig.update_layout(
            
            xaxis_title="Day of Week",
            yaxis_title="Total Menu Orders",
            barmode='group',  # จัดกลุ่มแท่งกราฟ
            template="plotly_white"
        )

        # แสดงกราฟ
        st.plotly_chart(fig)
                        

    # แสดงกราฟตามตัวเลือก
    if selected_chart == 'กราฟแสดงการเปรียบเทียบจำนวน Drinks Staff กับ ยอดขายทั้งหมด':
        one()
    elif selected_chart == 'กราฟแสดงการเปรียบเทียบจำนวน Drinks Staff กับ ยอดขายในแต่ละวัน':
        two()
    




col1,col2 = st.columns(2)

with col1:

    st.markdown(
        """
        <div style="text-align: center;">
            <strong>จำนวนพนักงานเฉลี่ยแต่ละเดือน</strong>
        </div>
        """,
        unsafe_allow_html=True
        )


    # สร้างคอลัมน์เดือนจากวันที่
    filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.to_period('M').astype(str)

    # คำนวณจำนวนพนักงานเฉลี่ยในแต่ละเดือนสำหรับ Kitchen Staff และ Drinks Staff
    kitchen_staff_avg = filtered_data.groupby('Month')['Kitchen Staff'].mean().reset_index()
    kitchen_staff_avg.columns = ['Month', 'Average Kitchen Staff']

    drinks_staff_avg = filtered_data.groupby('Month')['Drinks Staff'].mean().reset_index()
    drinks_staff_avg.columns = ['Month', 'Average Drinks Staff']

    # สร้าง Dropdown ใน Streamlit
    graph_option = st.selectbox(
        "Select Staff Type to Display:",
        options=['Kitchen Staff', 'Drinks Staff']
    )

    # เลือกข้อมูลและสร้างกราฟตามตัวเลือกใน Dropdown
    if graph_option == 'Kitchen Staff':
        fig = px.line(
            kitchen_staff_avg,
            x='Month',
            y='Average Kitchen Staff',
            markers=True,
            labels={'Average Kitchen Staff': 'Average Staff Count', 'Month': 'Month'},
            title="Average Monthly Kitchen Staff Count",
            template="plotly_white"
        )
    elif graph_option == 'Drinks Staff':
        fig = px.line(
            drinks_staff_avg,
            x='Month',
            y='Average Drinks Staff',
            markers=True,
            labels={'Average Drinks Staff': 'Average Staff Count', 'Month': 'Month'},
            title="Average Monthly Drinks Staff Count",
            template="plotly_white"
        )

    # แสดงกราฟใน Streamlit
    st.plotly_chart(fig)

with col2:

    
    st.markdown(
        """
        <div style="text-align: center;">
            <strong>เวลาเฉลี่ยนในการบริการ</strong>
        </div>
        """,
        unsafe_allow_html=True
        )


    # แปลงคอลัมน์วันที่และคำนวณความต่างระหว่างเวลา Serve และ Order
    filtered_data['Month'] = pd.to_datetime(filtered_data['Date']).dt.to_period('M').astype(str)
    filtered_data['Serve Duration'] = (pd.to_datetime(filtered_data['Serve Time']) - pd.to_datetime(filtered_data['Order Time'])).dt.total_seconds() / 60  # แปลงเป็นนาที

    # คำนวณเวลา Serve เฉลี่ยในแต่ละเดือน
    serve_time_avg = filtered_data.groupby('Month')['Serve Duration'].mean().reset_index()
    serve_time_avg.columns = ['Month', 'Average Serve Time (minutes)']

    # สร้างกราฟเส้นด้วย Plotly Express
    fig = px.line(
        serve_time_avg,
        x='Month',
        y='Average Serve Time (minutes)',
        markers=True,
        labels={'Average Serve Time (minutes)': 'Average Serve Time (minutes)', 'Month': 'Month'},
        title="Average Monthly Serve Time",
        template="plotly_white"
    )

    # แสดงกราฟใน Streamlit
    st.plotly_chart(fig)

        

    






