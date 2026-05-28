from rest_framework import serializers
from School.models import Plan , StudentSupport , PlanReport
from Account.models import User
from datetime import datetime, date


class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ['id' , 'student' , 'created_by' , 'lesson' ,
                  'date' , 'start' , 'end' , 
                  'test_number' ,'description' , 'created_at' , 'updated_at']
        

        read_only_fields = ['id' , 'created_by' , 'created_at' , 'updated_at']
        
        model = Plan

    def create(self, validated_data):
        created_by = self.context.get('user')
        validated_data['created_by'] = created_by
        return super().create(validated_data)    

class PlanReportSerializer(serializers.ModelSerializer):
    class Meta:

        fields = ['id' , 'student' , 'lesson' ,
                  'date' , 'start' , 'end' , 
                  'test_number' ,'description' , 'created_at' , 'updated_at']
        

        read_only_fields = ['id' , 'student' , 'created_at' , 'updated_at']
        model = PlanReport


    def create(self, validated_data):

        validated_data['duration'] = datetime.combine(date.today(), validated_data['end']) - datetime.combine(date.today(), validated_data['start'])

        return super().create(validated_data)    
    


class StudentSupportSerializer(serializers.Serializer):
    students = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="student") , many=True)
    support = serializers.PrimaryKeyRelatedField(queryset=User.objects.filter(role="support"))

    def create(self, validated_data):
        support = validated_data['support']
        students = validated_data['students']

        StudentSupport.objects.filter(support=support).delete()


        for student in students:
            StudentSupport.objects.create(
                support=support,
                student=student
            )

        return {
        "support": support,
        "students": [s for s in students]
        }
    





        
