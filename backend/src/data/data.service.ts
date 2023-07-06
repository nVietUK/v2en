import { Injectable } from '@nestjs/common';
import { DeepPartial, FindOptionsWhere } from 'typeorm';
import { Data } from './data.entity';
import { DataRepository } from './data.repository';

@Injectable()
export class DataService {
	constructor(private readonly dataRepository: DataRepository) {}

	async findAll(): Promise<Data[]> {
		return await this.dataRepository.find();
	}

	async findOneBy(args: FindOptionsWhere<Data>): Promise<Data> {
		return await this.dataRepository.findOneBy(args);
	}

	async createData(createDataInput: DeepPartial<Data>): Promise<Data> {
		const data = this.dataRepository.create(createDataInput);
		return await this.dataRepository.save(data);
	}

	async removeData(arg: FindOptionsWhere<Data>): Promise<Data> {
		const data = await this.findOneBy(arg);
		await this.dataRepository.remove(data);
		return new Data('', '', '', false);
	}
}
