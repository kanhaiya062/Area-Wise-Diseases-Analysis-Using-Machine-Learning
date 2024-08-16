from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

app = Flask(__name__)

# Mapping disease numbers to disease names
disease_map = {
    0: "Asthma",
    1: "Dengue",
    2: "Chikungunya",
    3: "Diabetes",
    4: "Rabies",
    5: "Kala-azar",
    6: "COVID",
    7: "Malaria",
    8: "Tuberculosis (TB)",
    9: "Typhoid Fever"
}

# Recommendations 
recommendations = {
    "Asthma": {
        "Low": "Carry an inhaler and avoid allergens.",
        "Medium": "Carry an inhaler and allergy medications.",
        "High": "Carry an inhaler, allergy medications, and a nebulizer."
    },
    "Dengue": {
        "Low": "Use mosquito repellents and carry a first aid kit.",
        "Medium": "Use mosquito repellents and carry oral rehydration salts.",
        "High": "Use mosquito repellents, carry oral rehydration salts, and seek immediate medical help if symptoms appear."
    },
    "Chikungunya": {
        "Low": "Use mosquito repellents and carry pain relief medication.",
        "Medium": "Use mosquito repellents and carry anti-inflammatory medication.",
        "High": "Use mosquito repellents, carry anti-inflammatory medication, and seek immediate medical help if symptoms appear."
    },
    "Diabetes": {
        "Low": "Carry glucose tablets and maintain a healthy diet.",
        "Medium": "Carry glucose tablets, insulin, and monitor blood sugar levels.",
        "High": "Carry glucose tablets, insulin, a glucometer, and seek immediate medical help if symptoms appear."
    },
    "Rabies": {
        "Low": "Avoid stray animals and ensure pets are vaccinated.",
        "Medium": "Avoid stray animals and carry rabies vaccination record.",
        "High": "Avoid stray animals, carry rabies vaccination record, and seek immediate medical help if bitten."
    },
    "Kala-azar": {
        "Low": "Use insect repellents and carry basic first aid kit.",
        "Medium": "Use insect repellents and carry antipyretic medication.",
        "High": "Use insect repellents, carry antipyretic medication, and seek immediate medical help if symptoms appear."
    },
    "COVID": {
        "Low": "Wear a mask and use hand sanitizer.",
        "Medium": "Wear a mask, use hand sanitizer, and carry a thermometer.",
        "High": "Wear a mask, use hand sanitizer, carry a thermometer, and seek immediate medical help if symptoms appear."
    },
    "Malaria": {
        "Low": "Use mosquito nets and carry insect repellent.",
        "Medium": "Use mosquito nets, carry insect repellent, and antimalarial drugs.",
        "High": "Use mosquito nets, carry insect repellent, antimalarial drugs, and seek immediate medical help if symptoms appear."
    },
    "Tuberculosis (TB)": {
        "Low": "Ensure proper ventilation and carry a mask.",
        "Medium": "Ensure proper ventilation, carry a mask, and take prescribed medications.",
        "High": "Ensure proper ventilation, carry a mask, take prescribed medications, and seek immediate medical help if symptoms appear."
    },
    "Typhoid Fever": {
        "Low": "Maintain good hygiene and carry bottled water.",
        "Medium": "Maintain good hygiene, carry bottled water, and antibiotics.",
        "High": "Maintain good hygiene, carry bottled water, antibiotics, and seek immediate medical help if symptoms appear."
    }
}

@app.route('/', methods=['GET', 'POST'])
def predict():
    if request.method == 'POST':
        state = request.form['state']
        disease = int(request.form['disease'])
        year = int(request.form['year'])

        # Load and preprocess data
        data = pd.read_csv('train_data.csv')
        for y in range(2018, 2025):
            data[str(y)] = data[str(y)].astype(int)

        # Filter data and get affected people
        state_disease_data = data[(data['State'] == state) & (data['Disease'] == disease)]
        if state_disease_data.empty:
            prediction = {
                'message': f"No data available for {disease_map[disease]} in {state} for the year {year}.",
                'rate': "N/A",
                'recommendation': "Please check the state and disease combination or try a different year.",
                'chart_url': None
            }
        else:
            # Get affected people
            affected_people = state_disease_data[str(year)].values[0]

            # Determine severity
            if affected_people < 100:
             severity = "Low"
            elif 100 <= affected_people < 500:
             severity = "Medium"
            else:
             severity = "High"

            # Generate chart
            disease_df = data[data['Disease'] == disease]
            melted_df = disease_df.melt(id_vars=['State', 'Disease', 'cluster'], var_name='Year', value_name='Cases')
            melted_df['Year'] = melted_df['Year'].astype(int)
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.scatterplot(x='Year', y='Cases', hue='cluster', style='State', data=melted_df, palette='tab10', s=100, ax=ax)
            ax.set_title(f'Disease Cases for {disease_map[disease]} Cluster-wise Year-wise')
            ax.set_xlabel('Year')
            ax.set_ylabel('Number of Cases')
            ax.legend(title='Cluster and State')
            ax.grid(True)
            chart_url = 'static/chart.png'
            fig.savefig(chart_url)

        #  estimated rate
            new_data = pd.read_csv('Disease-dataset.csv')
            total_population = new_data['No'].count()
            br_df = new_data[new_data['Area'] == state].count()
            total = br_df['Area'].sum()
            estimated_rate = (affected_people / total_population) * 100

        # Create prediction dictionary
            prediction = {
            'message': f"Number of people affected by {disease_map[disease]} in {state} in {year}: {affected_people} ({severity})",
            'rate': f"{estimated_rate:.3f}%",
            'recommendation': recommendations[disease_map[disease]][severity],
            'chart_url': chart_url
            }
        return render_template('index.html', prediction=prediction)

    return render_template('index.html')

if __name__ == '__main__':
    if os.environ.get('FLASK_ENV') == 'production':
        from waitress import serve
        serve(app, host='0.0.0.0', port=5000)
    else:
        app.run(debug=True)
