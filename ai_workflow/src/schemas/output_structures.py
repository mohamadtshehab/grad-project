from pydantic import BaseModel, Field
from typing import List

class Character(BaseModel):
    """Single character with name."""
    name: str = Field(description="اسم الشخصية")

class NameQuerier(BaseModel):
    """Use this schema to format the name query output."""
    characters: list[Character] = Field(description="قائمة بالشخصيات الموجودة في النص")
    
class ProfileData(BaseModel):
    """Single profile data for a character."""
    
    name: str = Field(
        description="اسم الشخصية كما هو مذكور في البروفايل المعطى؛ لا يتم تغييره"
    )
    
    age: str = Field(
        description="العمر التقديري أو الوصف الدال عليه إن وُجد في النص؛ إذا لم يكن واضحًا، تبقى القيمة كما هي"
    )
    
    role: str = Field(
        description="الدور الذي تلعبه الشخصية في النص (رئيسية، ثانوية، راوية، إلخ) إذا توفر في النص"
    )
    
    physical_characteristics: List[str] = Field(
        description="الصفات الجسدية التي وُصفت بها الشخصية بشكل صريح أو ضمني، بصيغة قائمة من النصوص"
    )
    
    personality: str = Field(
        description="الصفات النفسية أو السلوكية التي ظهرت في النص بوضوح أو تلميح"
    )
    
    events: List[str] = Field(
        description="قائمة بالأحداث المحورية والمهمة التي أثّرت على تطور الشخصية أو القصة؛ يتم تجاهل الأحداث التفصيلية أو العادية"
    )
    
    relations: List[str] = Field(
        description="قائمة بالعلاقات مع الشخصيات الأخرى بصيغة 'اسم_الشخصية: نوع_العلاقة' مثل 'سليم: صداقة'"
    )
    
    aliases: List[str] = Field(
        description="قائمة بالأسماء أو الألقاب الأخرى التي يُشار بها إلى الشخصية في النص"
    )
    
    id: str = Field(
        description="معرف فريد للشخصية؛ لا يتغير خلال التحديث"
    )


class ProfileRefresher(BaseModel):
    """Use this schema to format the profile refresher output."""
    profiles: List[ProfileData] = Field(description="قائمة من البروفايلات المحدثة للشخصيات")

class Summary(BaseModel):
    """Use this schema to format the summary output."""
    summary: str = Field(description="ملخص النص")

class BookNameExtractor(BaseModel):
    """Use this schema to format the book name extraction output."""
    book_name: str = Field(description="اسم الكتاب المستخرج من محتوى الملف")
    confidence: str = Field(description="مستوى الثقة في استخراج اسم الكتاب (عالي، متوسط، منخفض)")
    reasoning: str = Field(description="التفسير المنطقي لاختيار اسم الكتاب")

class TextQualityAssessment(BaseModel):
    """Use this schema to format the text quality assessment output."""
    quality_score: float = Field(description="درجة جودة النص من 0 إلى 1 (1 = ممتاز، 0 = سيء جداً)")
    quality_level: str = Field(description="مستوى الجودة (ممتاز، جيد، متوسط، سيء، سيء جداً)")
    issues: List[str] = Field(description="قائمة بالمشاكل المكتشفة في النص")
    suggestions: List[str] = Field(description="قائمة بالاقتراحات لتحسين جودة النص")
    reasoning: str = Field(description="التفسير المنطقي لتقييم جودة النص")


class TextClassification(BaseModel):
    """Use this schema to format the text classification output."""
    is_literary: bool = Field(description="هل النص أدبي أم لا (true = أدبي، false = غير أدبي)")
    classification: str = Field(description="تصنيف النص (أدبي، علمي، إخباري، تقني، ديني، تاريخي، إلخ)")
    confidence: float = Field(description="مستوى الثقة في التصنيف من 0 إلى 1")
    reasoning: str = Field(description="التفسير المنطقي لتصنيف النص")
    literary_features: List[str] = Field(description="قائمة بالخصائص الأدبية الموجودة في النص (إذا كان أدبياً)")
    non_literary_features: List[str] = Field(description="قائمة بالخصائص غير الأدبية الموجودة في النص (إذا لم يكن أدبياً)")

class EmptyProfileValidation(BaseModel):
    """Use this schema to format the empty profile validation output."""
    has_empty_profiles: bool = Field(description="هل توجد بروفايلات فارغة")
    empty_profiles: List[str] = Field(description="قائمة بأسماء البروفايلات الفارغة")
    suggestions: List[str] = Field(description="اقتراحات لتحسين البروفايلات")
    profiles: List[ProfileData] = Field(description="قائمة من البروفايلات المحدثة للشخصيات")
    validation_score: float = Field(description="درجة جودة البروفايلات من 0 إلى 1")
