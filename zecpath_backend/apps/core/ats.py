def calculate_ats_score(candidate_data, job):
    score = 0

    candidate_skills = set(candidate_data.get("skills", []))
    job_skills = set(job.skills.split(","))

    matched_skills = candidate_skills.intersection(job_skills)

    if job_skills:
        skill_score = (len(matched_skills) / len(job_skills)) * 60
    else:
        skill_score = 0

    score += skill_score

    if candidate_data.get("experience") != "Fresher":
        score += 25

    if "B.Tech" in candidate_data.get("education", []):
        score += 15

    return round(score, 2)