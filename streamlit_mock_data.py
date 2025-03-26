import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta


def add_comment_section():
    """
    Adds a comment section to the dashboard where users can leave feedback or notes,
    and simulates receiving email replies.
    """
    st.markdown("---")
    st.subheader("Comments & Notes")

    # Create tabs for different comment sources
    comment_tab1, comment_tab2 = st.tabs(
        ["Dashboard Comments", "Email Replies"])

    with comment_tab1:
        # Initialize comments in session state if they don't exist
        if 'comments' not in st.session_state:
            st.session_state.comments = []

        # Text input for new comments
        comment_text = st.text_area("Add a new comment or note:", height=100)

        # Add comment button
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("Add Comment"):
                if comment_text.strip():  # Check if comment is not empty
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    st.session_state.comments.append({
                        "text": comment_text,
                        "timestamp": timestamp,
                        "source": "dashboard"
                    })
                    st.success("Comment added!")

        # Show existing dashboard comments
        if st.session_state.comments:
            dashboard_comments = [
                c for c in st.session_state.comments if c.get('source') != 'email']

            if dashboard_comments:
                st.markdown("### Dashboard Comments")
                for i, comment in enumerate(dashboard_comments):
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                        <small>{comment['timestamp']}</small>
                        <p>{comment['text']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Allow comment deletion
                    if st.button(f"Delete", key=f"delete_dash_{i}"):
                        st.session_state.comments.remove(comment)
                        st.experimental_rerun()
            else:
                st.info("No dashboard comments yet. Add a comment above.")

    with comment_tab2:
        # Simulate receiving an email reply
        st.markdown("### Simulate Email Reply")
        st.info("This simulates a user replying to a dashboard email")

        # Input fields to simulate an email reply
        reply_email = st.text_input(
            "Reply From:", value="dimitrios@company.com")
        reply_subject = st.text_input(
            "Reply Subject:", value="RE: SaaS Sales Dashboard Report")
        reply_content = st.text_area(
            "Email Reply Content:", value="I noticed the Q3 numbers look significantly better than projected. Great work!")

        # Button to "receive" the simulated email reply
        if st.button("Simulate Receiving Email Reply"):
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Add to comments with special formatting to indicate it came via email
            if 'comments' not in st.session_state:
                st.session_state.comments = []

            st.session_state.comments.append({
                "text": reply_content,
                "timestamp": timestamp,
                "source": "email",
                "sender": reply_email,
                "subject": reply_subject
            })

            st.success("Email reply received and added to comments!")

        # Show existing email comments
        if st.session_state.comments:
            email_comments = [
                c for c in st.session_state.comments if c.get('source') == 'email']

            if email_comments:
                st.markdown("### Email Replies")
                for i, comment in enumerate(email_comments):
                    st.markdown(f"""
                    <div style="padding: 10px; border-radius: 5px; border: 1px solid #4285F4; background-color: #E8F0FE; margin-bottom: 10px;">
                        <small>📧 Email reply from {comment['sender']} - {comment['timestamp']}</small>
                        <small>Subject: {comment['subject']}</small>
                        <p style="margin-top: 5px; margin-bottom: 0;">{comment['text']}</p>
                    </div>
                    """, unsafe_allow_html=True)

                    # Allow email reply deletion
                    if st.button(f"Delete", key=f"delete_email_{i}"):
                        st.session_state.comments.remove(comment)
                        st.experimental_rerun()
            else:
                st.info("No email replies yet. Simulate one above.")

    # Show all comments together option
    show_all = st.checkbox("Show all comments together")

    if show_all and st.session_state.comments:
        st.markdown("### All Comments")

        # Sort all comments by timestamp
        all_comments = sorted(st.session_state.comments,
                              key=lambda x: x['timestamp'], reverse=True)

        for i, comment in enumerate(all_comments):
            # Special formatting for email-sourced comments
            if comment.get('source') == 'email':
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border: 1px solid #4285F4; background-color: #E8F0FE; margin-bottom: 10px;">
                    <small>📧 Email reply from {comment['sender']} - {comment['timestamp']}</small>
                    <p style="margin-top: 5px; margin-bottom: 0;">{comment['text']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # Regular comment display
                st.markdown(f"""
                <div style="padding: 10px; border-radius: 5px; border: 1px solid #ddd; margin-bottom: 10px;">
                    <small>💬 Dashboard comment - {comment['timestamp']}</small>
                    <p>{comment['text']}</p>
                </div>
                """, unsafe_allow_html=True)


def add_segment_performance_view(filtered_sales):
    """
    Creates a granular view of performance data grouped by segment, with color-coded
    indicators for month-over-month (MoM) and week-over-week (WoW) changes.
    """
    st.subheader("Segment Performance Analysis")

    # Select segment type
    segment_type = st.selectbox(
        "Group performance by:",
        options=["Product", "Region", "Channel", "Customer Type"]
    )

    # Add time frame selection
    current_date = datetime.now().date()
    end_date = current_date
    start_date = end_date - timedelta(days=90)  # Default to last 90 days

    # Prepare data
    # Add week and month fields
    filtered_sales['Week'] = filtered_sales['Date'].dt.isocalendar().week
    filtered_sales['Year_Week'] = filtered_sales['Date'].dt.year.astype(
        str) + "-W" + filtered_sales['Week'].astype(str).str.zfill(2)
    filtered_sales['Year_Month'] = filtered_sales['Date'].dt.year.astype(
        str) + "-" + filtered_sales['Date'].dt.month.astype(str).str.zfill(2)

    # Get unique weeks and months
    weeks = sorted(filtered_sales['Year_Week'].unique())
    months = sorted(filtered_sales['Year_Month'].unique())

    # Only proceed if we have enough data
    if len(weeks) >= 2 and len(months) >= 2:
        # Get the last two weeks and months
        current_week, previous_week = weeks[-1], weeks[-2]
        current_month, previous_month = months[-1], months[-2]

        # Group by segment and time period
        segment_current_week = filtered_sales[filtered_sales['Year_Week'] == current_week].groupby(
            segment_type)['Revenue'].sum()
        segment_previous_week = filtered_sales[filtered_sales['Year_Week'] == previous_week].groupby(segment_type)[
            'Revenue'].sum()

        segment_current_month = filtered_sales[filtered_sales['Year_Month'] == current_month].groupby(segment_type)[
            'Revenue'].sum()
        segment_previous_month = filtered_sales[filtered_sales['Year_Month'] == previous_month].groupby(segment_type)[
            'Revenue'].sum()

        # Create performance dataframe
        performance_data = []

        for segment in filtered_sales[segment_type].unique():
            # Calculate WoW and MoM changes
            wow_value = segment_current_week.get(segment, 0)
            prev_wow_value = segment_previous_week.get(segment, 0)
            wow_change = ((wow_value - prev_wow_value) /
                          prev_wow_value * 100) if prev_wow_value > 0 else 0

            mom_value = segment_current_month.get(segment, 0)
            prev_mom_value = segment_previous_month.get(segment, 0)
            mom_change = ((mom_value - prev_mom_value) /
                          prev_mom_value * 100) if prev_mom_value > 0 else 0

            performance_data.append({
                'Segment': segment,
                'Current Revenue': wow_value,
                'WoW Change (%)': wow_change,
                'MoM Change (%)': mom_change
            })

        performance_df = pd.DataFrame(performance_data)

        # Display the performance table with color coding
        st.write(f"### {segment_type} Performance")
        st.write(
            f"Current Week: {current_week} | Current Month: {current_month}")

        # Format the dataframe
        def color_change(val):
            color = 'green' if val > 0 else 'red' if val < 0 else 'black'
            return f'color: {color}; font-weight: bold'

        # Apply styling
        styled_df = performance_df.style.\
            format({'Current Revenue': '${:,.2f}', 'WoW Change (%)': '{:+.2f}%', 'MoM Change (%)': '{:+.2f}%'}).\
            applymap(color_change, subset=['WoW Change (%)', 'MoM Change (%)'])

        st.dataframe(styled_df, use_container_width=True)

        # Add a visualization
        fig = px.bar(
            performance_df,
            x='Segment',
            y='Current Revenue',
            color='MoM Change (%)',
            color_continuous_scale=['red', 'yellow', 'green'],
            range_color=[-20, 20],  # Set range for color scale
            title=f"Current Revenue by {segment_type} with MoM Change",
            text='MoM Change (%)'
        )

        fig.update_traces(texttemplate='%{text:.1f}%', textposition='outside')
        fig.update_layout(height=500)

        st.plotly_chart(fig, use_container_width=True)

        # Add insight
        best_segment = performance_df.loc[performance_df['MoM Change (%)'].idxmax(
        )]['Segment']
        worst_segment = performance_df.loc[performance_df['MoM Change (%)'].idxmin(
        )]['Segment']

        st.info(f"""
        **Quick Insights:**
        - Best performing {segment_type.lower()}: **{best_segment}** (MoM: {performance_df.loc[performance_df['MoM Change (%)'].idxmax()]['MoM Change (%)']:.1f}%)
        - Needs attention: **{worst_segment}** (MoM: {performance_df.loc[performance_df['MoM Change (%)'].idxmin()]['MoM Change (%)']:.1f}%)
        """)
    else:
        st.warning(
            "Not enough data to calculate week-over-week or month-over-month changes. Need at least 2 months of data.")


def add_export_options(data, prefix="data"):
    """
    Adds export options (CSV/Excel) for the provided dataframe.

    Parameters:
    -----------
    data : pandas.DataFrame
        The dataframe to be exported
    prefix : str
        Prefix for the exported filename
    """
    import io

    st.subheader("Export Options")

    # Options for export
    export_type = st.radio(
        "Select export format:",
        options=["CSV", "Excel"],
        horizontal=True
    )

    # Show preview
    st.write("Preview (first 5 rows):")
    st.dataframe(data.head())

    # Generate timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    if export_type == "CSV":
        # Convert to CSV
        csv = data.to_csv(index=False).encode('utf-8')

        # Download button
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"{prefix}_{timestamp}.csv",
            mime="text/csv"
        )
    else:  # Excel
        try:
            # Convert to Excel
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                data.to_excel(writer, index=False, sheet_name='Data')

                # Access the XlsxWriter workbook and worksheet objects
                workbook = writer.book
                worksheet = writer.sheets['Data']

                # Add some cell formats
                header_format = workbook.add_format({
                    'bold': True,
                    'bg_color': '#D3D3D3',
                    'border': 1
                })

                # Write the column headers with the defined format
                for col_num, value in enumerate(data.columns.values):
                    worksheet.write(0, col_num, value, header_format)
                    # Set column width based on content
                    worksheet.set_column(
                        col_num, col_num, max(len(str(value)), 10))

            excel_data = buffer.getvalue()

            # Download button
            st.download_button(
                label="Download Excel",
                data=excel_data,
                file_name=f"{prefix}_{timestamp}.xlsx",
                mime="application/vnd.ms-excel"
            )
        except Exception as e:
            st.error(f"Excel export failed: {e}")
            st.info(
                "Please make sure xlsxwriter is installed: pip install xlsxwriter")


def simulate_email_reply():
    st.markdown("### Simulate Email Reply")
    st.info("This simulates a user replying to a dashboard email")

    # Input fields to simulate an email reply
    reply_email = st.text_input("Reply From:", value="colleague@company.com")
    reply_subject = st.text_input(
        "Reply Subject:", value="RE: SaaS Sales Dashboard Report")
    reply_content = st.text_area(
        "Email Reply Content:", value="I noticed the Q3 numbers look significantly better than projected. Great work!")

    # Button to "receive" the simulated email reply
    if st.button("Simulate Receiving Email Reply"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add to comments with special formatting to indicate it came via email
        if 'comments' not in st.session_state:
            st.session_state.comments = []

        st.session_state.comments.append({
            "text": reply_content,
            "timestamp": timestamp,
            "source": "email",
            "sender": reply_email,
            "subject": reply_subject
        })

        st.success("Email reply received and added to comments!")


def add_email_dashboard():
    """
    Adds an email feature to the dashboard that simulates sending the dashboard data,
    visualizations, and comments via email.
    """
    st.markdown("---")
    st.subheader("📧 Email Dashboard Report")

    # Input fields for email
    recipient_email = st.text_input(
        "Recipient Email Address:", placeholder="Dimitrios@company.com")
    email_subject = st.text_input(
        "Email Subject:", value="SaaS Sales Dashboard Report")

    # Select what to include in the email
    st.write("Select items to include in the email:")
    include_data = st.checkbox("Include Data (Excel)", value=True)
    include_viz = st.checkbox("Include Visualizations (PNG)", value=True)
    include_comments = st.checkbox("Include Comments", value=True)

    # Additional message
    email_message = st.text_area("Additional Message:",
                                 value="Please find attached the latest SaaS sales dashboard report.")

    # Preview email content
    if st.button("Preview Email"):
        st.success("Email Preview Generated")

        preview_col1, preview_col2 = st.columns([1, 2])

        with preview_col1:
            st.markdown("### Email Metadata")
            st.markdown(f"**To:** {recipient_email}")
            st.markdown(f"**Subject:** {email_subject}")
            st.markdown(f"**From:** dashboard@VRBLSM.com")
            st.markdown(
                f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")

        with preview_col2:
            st.markdown("### Email Content")
            st.markdown(email_message)

            attachments = []
            if include_data:
                attachments.append("📊 saas_sales_data.xlsx")
            if include_viz:
                attachments.append("📈 revenue_trend.png")
                attachments.append("🥧 product_distribution.png")
            if include_comments and 'comments' in st.session_state and st.session_state.comments:
                comments_text = "\n\n### Dashboard Comments:\n\n"
                for comment in st.session_state.comments:
                    comments_text += f"- {comment['timestamp']}: {comment['text']}\n\n"
                st.markdown(comments_text)

            if attachments:
                st.markdown("### Attachments")
                for attachment in attachments:
                    st.markdown(f"- {attachment}")

    # Send email button
    if st.button("Send Email"):
        if not recipient_email or "@" not in recipient_email:
            st.error("Please enter a valid email address.")
        else:
            # In a real implementation, this is where you would call your email sending code
            # For the demo, we'll just show a success message
            st.success(f"✅ Email successfully sent to {recipient_email}!")
            st.info("Note: This is a demo feature. No actual email was sent.")

            # You could store sent emails in session state for the demo
            if 'sent_emails' not in st.session_state:
                st.session_state.sent_emails = []

            st.session_state.sent_emails.append({
                "recipient": recipient_email,
                "subject": email_subject,
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            })


def generate_mock_data():
    np.random.seed(42)
    dates = pd.date_range(start=datetime.now() -
                          timedelta(days=365), end=datetime.now(), freq='D')
    products = ["Enterprise", "Professional", "Starter"]
    regions = ["North America", "Europe", "Asia Pacific", "Latin America"]

    data = []
    for date in dates:
        for product in products:
            for region in regions:
                if np.random.random() > 0.7:  # Not every day has data
                    price = 1000 if product == "Enterprise" else 200 if product == "Professional" else 50
                    quantity = np.random.randint(1, 20)
                    revenue = price * quantity
                    cost = revenue * 0.4
                    data.append({
                        "Date": date,
                        "Product": product,
                        "Region": region,
                        "Revenue": revenue,
                        "Cost": cost,
                        "Profit": revenue - cost
                    })

    return pd.DataFrame(data)


# Generate data
sales_df = generate_mock_data()

# Title
st.title("SaaS Sales Dashboard")

# Date filter
min_date, max_date = sales_df["Date"].min(
).date(), sales_df["Date"].max().date()
date_range = st.sidebar.date_input(
    "Select Date Range", [min_date, max_date], min_date, max_date)

# Filter data
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered_sales = sales_df[(sales_df["Date"].dt.date >= start_date) & (
        sales_df["Date"].dt.date <= end_date)]
else:
    filtered_sales = sales_df

# Filters for region and product
regions = st.sidebar.multiselect(
    "Select Regions", options=sales_df["Region"].unique(), default=sales_df["Region"].unique())
products = st.sidebar.multiselect(
    "Select Products", options=sales_df["Product"].unique(), default=sales_df["Product"].unique())

if regions:
    filtered_sales = filtered_sales[filtered_sales["Region"].isin(regions)]
if products:
    filtered_sales = filtered_sales[filtered_sales["Product"].isin(products)]

# Key Metrics
total_revenue = filtered_sales["Revenue"].sum()
total_profit = filtered_sales["Profit"].sum()
profit_margin = (total_profit / total_revenue *
                 100) if total_revenue > 0 else 0

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Revenue", f"${total_revenue:,.2f}")
with col2:
    st.metric("Total Profit", f"${total_profit:,.2f}")
with col3:
    st.metric("Profit Margin", f"{profit_margin:.2f}%")

# Create tabs for different views
tab1, tab2, tab3 = st.tabs(["Overview", "Detailed Analysis", "Executive View"])

with tab1:
    # Revenue over time
    revenue_by_date = filtered_sales.groupby(filtered_sales["Date"].dt.date)[
        "Revenue"].sum().reset_index()
    fig1 = px.line(revenue_by_date, x="Date",
                   y="Revenue", title="Daily Revenue")
    st.plotly_chart(fig1, use_container_width=True)

    # Revenue by product and region
    col1, col2 = st.columns(2)
    with col1:
        product_revenue = filtered_sales.groupby(
            "Product")["Revenue"].sum().reset_index()
        fig2 = px.pie(product_revenue, values="Revenue",
                      names="Product", title="Revenue by Product")
        st.plotly_chart(fig2, use_container_width=True)
    with col2:
        region_revenue = filtered_sales.groupby(
            "Region")["Revenue"].sum().reset_index()
        fig3 = px.bar(region_revenue, x="Region", y="Revenue",
                      title="Revenue by Region", color="Region")
        st.plotly_chart(fig3, use_container_width=True)

with tab2:
    # Granular analysis
    granularity = st.selectbox("Select Time Granularity", [
                               "Daily", "Weekly", "Monthly"])

    if granularity == "Daily":
        granular_data = filtered_sales.groupby(filtered_sales["Date"].dt.date)[
            "Revenue"].sum().reset_index()
        x_col = "Date"
    elif granularity == "Weekly":
        filtered_sales["Week"] = filtered_sales["Date"].dt.strftime('%Y-W%U')
        granular_data = filtered_sales.groupby(
            "Week")["Revenue"].sum().reset_index()
        x_col = "Week"
    else:  # Monthly
        filtered_sales["Month"] = filtered_sales["Date"].dt.strftime('%Y-%m')
        granular_data = filtered_sales.groupby(
            "Month")["Revenue"].sum().reset_index()
        x_col = "Month"

    fig4 = px.line(granular_data, x=x_col, y="Revenue",
                   title=f"{granularity} Revenue", markers=True)
    st.plotly_chart(fig4, use_container_width=True)

    # Data table
    st.subheader("Detailed Data")
    st.dataframe(filtered_sales.sort_values("Date", ascending=False).head(100))
    add_segment_performance_view(filtered_sales)


with tab3:
    # Executive View for CP4
    st.subheader("Executive Dashboard")

    # Period over period analysis
    if not filtered_sales.empty:
        mid_point = min(
            filtered_sales["Date"]) + (max(filtered_sales["Date"]) - min(filtered_sales["Date"])) / 2
        first_half = filtered_sales[filtered_sales["Date"] <= mid_point]
        second_half = filtered_sales[filtered_sales["Date"] > mid_point]

        first_half_revenue = first_half["Revenue"].sum(
        ) if not first_half.empty else 0
        second_half_revenue = second_half["Revenue"].sum(
        ) if not second_half.empty else 0
        revenue_growth = ((second_half_revenue - first_half_revenue) /
                          first_half_revenue * 100) if first_half_revenue > 0 else 0

        growth_color = "green" if revenue_growth > 0 else "red"
        growth_arrow = "↑" if revenue_growth > 0 else "↓"

        st.markdown(f"""
        <div style="padding: 20px; border-radius: 5px; background: white; border: 1px solid #ddd; margin-bottom: 20px;">
            <h3>Revenue Growth</h3>
            <p style="font-size: 2rem; color: {growth_color};">{abs(revenue_growth):.1f}% {growth_arrow}</p>
            <p>Period over Period</p>
        </div>
        """, unsafe_allow_html=True)

        # Top performers
        top_product = filtered_sales.groupby("Product")["Revenue"].sum(
        ).idxmax() if not filtered_sales.empty else "N/A"
        top_region = filtered_sales.groupby("Region")["Revenue"].sum(
        ).idxmax() if not filtered_sales.empty else "N/A"

        st.markdown(f"""
        ### Key Highlights
        
        - **Top Product**: {top_product}
        - **Top Region**: {top_region}
        - **Revenue Growth**: {revenue_growth:.1f}%
        - **Profit Margin**: {profit_margin:.1f}%
        """)
        add_comment_section()
        add_email_dashboard()
