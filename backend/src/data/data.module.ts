import { Module } from '@nestjs/common';
import { DataResolver } from './data.resolver';
import { DataService } from './data.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { Data } from './data.entity';
import { DataController } from './data.controller';

@Module({
	providers: [DataResolver, DataService],
	imports: [TypeOrmModule.forFeature([Data]), TypeOrmModule.forRoot()],
	controllers: [DataController],
})
export class DataModule {}
