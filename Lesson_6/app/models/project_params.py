from pydantic import BaseModel


class ProjectParams(BaseModel):

    blurb: str
    currency: str
    goal: float
    campaign_duration: int
    started_month: int
    category_subcategory: str

    def to_list(self) -> list[float]:
        return [
            self.blurb,
            self.currency,
            self.goal,
            self.campaign_duration,
            self.started_month,
            self.category_subcategory,
        ]
